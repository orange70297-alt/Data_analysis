# -*- coding: utf-8 -*-
"""
RFM 分析腳本：Online Retail 數據集
依據「分析策略建議_1.md」方案一，產出客群區隔與沈睡 VIP 名單及關鍵洞察。
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime

# 路徑設定（以專案根目錄為基準）
# 本腳本位於：<專案根>/案例A_Online_Retail_RFM/02數據分析/
# 因此往上兩層即可回到專案根目錄。
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(ROOT, "資料集", "Online Retail", "online_retail_1.csv")
OUTPUT_DIR = os.path.dirname(__file__)


def load_and_clean(df_path: str) -> pd.DataFrame:
    """
    依數據卡建議：讀取資料、解析日期、排除無效交易與缺失 CustomerID。
    - 原始檔為「明細」層級（每列一筆商品），百萬筆 = 明細筆數。
    - 排除 CustomerID 空值（約 22.77%）後，再排除 Quantity<=0、UnitPrice<=0 或 >=10000。
    - 有效分析樣本 = 不重複 CustomerID 數（約 5,877 人），非明細筆數。
    """
    df = pd.read_csv(df_path, encoding="utf-8", low_memory=False)
    # 日期解析（格式 12/1/2009 7:45）
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="mixed", dayfirst=False)
    df = df.dropna(subset=["CustomerID"])
    df["CustomerID"] = df["CustomerID"].astype(int)
    # 僅保留正常銷售：數量與單價為正，並排除極端單價
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0) & (df["UnitPrice"] < 10000)]
    df["Amount"] = df["Quantity"] * df["UnitPrice"]
    return df


def compute_rfm(df: pd.DataFrame, ref_date: pd.Timestamp) -> pd.DataFrame:
    """以客戶為單位計算 Recency、Frequency、Monetary。"""
    agg = df.groupby("CustomerID").agg(
        LastOrderDate=("InvoiceDate", "max"),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Amount", "sum"),
    ).reset_index()
    agg["Recency"] = (ref_date - agg["LastOrderDate"]).dt.days
    rfm = agg[["CustomerID", "Recency", "Frequency", "Monetary"]].copy()
    return rfm


def assign_rfm_quintiles(rfm: pd.DataFrame) -> pd.DataFrame:
    """R/F/M 依五分位分箱，1=最差、5=最佳。Recency 愈大愈差故取反序。"""
    rfm = rfm.copy()
    rfm["R_quintile"] = pd.qcut(rfm["Recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop")
    rfm["F_quintile"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    rfm["M_quintile"] = pd.qcut(rfm["Monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    rfm["R_quintile"] = rfm["R_quintile"].astype(int)
    rfm["F_quintile"] = rfm["F_quintile"].astype(int)
    rfm["M_quintile"] = rfm["M_quintile"].astype(int)
    return rfm


def assign_segment(rfm: pd.DataFrame, dormant_days: int = 90) -> pd.DataFrame:
    """
    依 R/F/M 與 Recency 天數定義 4–6 個可操作區隔。
    沈睡 VIP：高 F、高 M，且最後購買距今 >= dormant_days 天。
    """
    rfm = rfm.copy()

    def segment(row):
        r, f, m = row["R_quintile"], row["F_quintile"], row["M_quintile"]
        rec = row["Recency"]
        is_dormant = rec >= dormant_days
        if is_dormant and f >= 4 and m >= 4:
            return "沈睡 VIP"
        if not is_dormant and f >= 4 and m >= 4:
            return "活躍 VIP"
        if not is_dormant and f <= 2 and m <= 3:
            return "潛力新客"
        if is_dormant and (f < 4 or m < 4):
            return "一般流失"
        if not is_dormant and (f >= 3 or m >= 3):
            return "一般活躍"
        return "其他"

    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm


def main():
    print("載入與清洗資料...")
    df = load_and_clean(DATA_PATH)
    ref_date = df["InvoiceDate"].max()
    print(f"參考日期（分析基準日）: {ref_date.date()}")
    print(f"有效交易筆數: {len(df):,}，客戶數: {df['CustomerID'].nunique():,}")

    print("計算 RFM...")
    rfm = compute_rfm(df, ref_date)
    rfm = assign_rfm_quintiles(rfm)
    rfm = assign_segment(rfm, dormant_days=90)

    # 各客群規模與營收貢獻表
    segment_summary = (
        rfm.groupby("Segment", as_index=False)
        .agg(
            CustomerCount=("CustomerID", "count"),
            TotalRevenue=("Monetary", "sum"),
            AvgMonetary=("Monetary", "mean"),
        )
        .assign(RevenuePct=lambda x: (x["TotalRevenue"] / x["TotalRevenue"].sum() * 100).round(2))
        .assign(CustomerPct=lambda x: (x["CustomerCount"] / x["CustomerCount"].sum() * 100).round(2))
    )
    segment_summary = segment_summary.sort_values("TotalRevenue", ascending=False)

    total_revenue = rfm["Monetary"].sum()
    total_customers = len(rfm)

    # 沈睡 VIP 單獨統計
    sleep_vip = rfm[rfm["Segment"] == "沈睡 VIP"]
    sleep_vip_count = len(sleep_vip)
    sleep_vip_revenue = sleep_vip["Monetary"].sum()
    sleep_vip_revenue_pct = (sleep_vip_revenue / total_revenue * 100) if total_revenue else 0
    sleep_vip_avg = sleep_vip["Monetary"].mean() if len(sleep_vip) else 0

    # 沈睡 VIP 名單（依營收排序，供發券使用）
    sleep_vip_list = (
        sleep_vip[["CustomerID", "Recency", "Frequency", "Monetary"]]
        .sort_values("Monetary", ascending=False)
        .reset_index(drop=True)
    )
    sleep_vip_list = sleep_vip_list.rename(columns={"Monetary": "TotalAmount"})

    # 輸出檔案
    segment_summary.to_csv(os.path.join(OUTPUT_DIR, "rfm_segment_summary.csv"), index=False, encoding="utf-8-sig")
    sleep_vip_list.to_csv(os.path.join(OUTPUT_DIR, "sleep_vip_list.csv"), index=False, encoding="utf-8-sig")
    rfm.to_csv(os.path.join(OUTPUT_DIR, "rfm_customer_table.csv"), index=False, encoding="utf-8-sig")

    # 彙總數字供洞察報告使用
    insights = {
        "ref_date": ref_date.date().isoformat(),
        "total_customers": total_customers,
        "total_revenue": round(total_revenue, 2),
        "segment_summary": segment_summary,
        "sleep_vip_count": sleep_vip_count,
        "sleep_vip_revenue": round(sleep_vip_revenue, 2),
        "sleep_vip_revenue_pct": round(sleep_vip_revenue_pct, 2),
        "sleep_vip_avg": round(sleep_vip_avg, 2),
        "sleep_vip_list": sleep_vip_list,
    }
    return insights


if __name__ == "__main__":
    insights = main()
    print("\n--- 客群摘要 ---")
    print(insights["segment_summary"].to_string(index=False))
    print("\n--- 沈睡 VIP 關鍵指標 ---")
    print(f"人數: {insights['sleep_vip_count']:,}，營收貢獻佔比: {insights['sleep_vip_revenue_pct']}%，平均客單價: {insights['sleep_vip_avg']:,.2f}")
