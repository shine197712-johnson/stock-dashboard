"""
📊 股市观察 v3.7
专业级数据源架构 - 多源冗余 + 智能降级
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="股市观察 - 全球行情与资讯",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Apple风格CSS ====================
st.markdown("""
<style>
.stApp { background: #000000; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }

* { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif; }

[data-testid="stSidebar"] { background: #1c1c1e; border-right: 1px solid #2c2c2e; }
[data-testid="stSidebar"] * { color: #f5f5f7 !important; }

.main-title { font-size: 48px; font-weight: 700; color: #f5f5f7; text-align: center; letter-spacing: -0.5px; margin-bottom: 8px; }
.sub-title { font-size: 17px; font-weight: 400; color: #86868b; text-align: center; margin-bottom: 40px; }
.section-header { font-size: 28px; font-weight: 600; color: #f5f5f7; margin: 40px 0 20px 0; }

.index-card {
    background: rgba(28, 28, 30, 0.8);
    backdrop-filter: blur(20px);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
}
.index-card:hover { transform: scale(1.02); background: rgba(44, 44, 46, 0.9); }
.index-region { font-size: 13px; font-weight: 500; color: #86868b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.index-name { font-size: 15px; font-weight: 600; color: #f5f5f7; margin-bottom: 8px; }
.index-price { font-size: 28px; font-weight: 700; color: #f5f5f7; letter-spacing: -0.5px; }
.index-change { font-size: 15px; font-weight: 500; margin-top: 4px; }

.up { color: #34c759; }
.down { color: #ff3b30; }
.neutral { color: #86868b; }

.futures-card {
    background: rgba(28, 28, 30, 0.6);
    backdrop-filter: blur(20px);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.futures-name { font-size: 13px; color: #86868b; margin-bottom: 4px; }
.futures-price { font-size: 20px; font-weight: 600; color: #f5f5f7; }
.futures-change { font-size: 13px; font-weight: 500; }

.news-section-title { font-size: 22px; font-weight: 600; color: #f5f5f7; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #2c2c2e; }
.news-card { background: rgba(28, 28, 30, 0.5); border-radius: 12px; padding: 16px; margin-bottom: 8px; border: 1px solid rgba(255, 255, 255, 0.06); transition: all 0.2s ease; }
.news-card:hover { background: rgba(44, 44, 46, 0.7); }
.news-number { font-size: 12px; font-weight: 600; color: #0a84ff; margin-bottom: 6px; }
.news-title { font-size: 14px; font-weight: 500; color: #f5f5f7; line-height: 1.5; margin-bottom: 8px; }
.news-meta { font-size: 12px; color: #86868b; }

.tag { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; margin-right: 8px; }
.tag-politics { background: rgba(255, 59, 48, 0.15); color: #ff453a; }
.tag-economy { background: rgba(255, 159, 10, 0.15); color: #ff9f0a; }
.tag-tech { background: rgba(10, 132, 255, 0.15); color: #0a84ff; }

.divider { height: 1px; background: linear-gradient(90deg, transparent, #3a3a3c, transparent); margin: 40px 0; }
.footer-info { text-align: center; color: #86868b; font-size: 12px; padding: 40px 0 20px 0; }

.stock-card { background: rgba(28, 28, 30, 0.8); backdrop-filter: blur(20px); border-radius: 18px; padding: 24px; margin-bottom: 16px; border: 1px solid rgba(255, 255, 255, 0.1); }
.stock-name { font-size: 17px; font-weight: 600; color: #f5f5f7; }
.stock-code { font-size: 13px; color: #86868b; }
.stock-price { font-size: 34px; font-weight: 700; letter-spacing: -1px; margin: 12px 0; }
.stock-detail { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #2c2c2e; }
.stock-detail:last-child { border-bottom: none; }
.detail-label { font-size: 13px; color: #86868b; }
.detail-value { font-size: 13px; color: #f5f5f7; font-weight: 500; }

.timestamp { font-size: 12px; color: #48484a; text-align: right; margin-top: 20px; }
.empty-state { text-align: center; padding: 60px 20px; color: #86868b; }
.empty-state-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state-text { font-size: 17px; font-weight: 500; }

.data-source { font-size: 10px; color: #3a3a3c; margin-top: 4px; }

.stButton > button { background: rgba(10, 132, 255, 0.1) !important; color: #0a84ff !important; border: 1px solid rgba(10, 132, 255, 0.3) !important; border-radius: 10px !important; }
.stButton > button:hover { background: rgba(10, 132, 255, 0.2) !important; }
.stTextInput > div > div > input { background: #1c1c1e !important; color: #f5f5f7 !important; border: 1px solid #3a3a3c !important; border-radius: 10px !important; }
.stExpander { background: rgba(28, 28, 30, 0.5) !important; border: 1px solid #2c2c2e !important; border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ==================== 专业级数据获取模块 ====================

class GlobalMarketData:
    """全球市场数据聚合器 - 多数据源冗余架构"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.timeout = 8
    
    def _safe_request(self, url, params=None, headers=None):
        """安全请求封装"""
        try:
            resp = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except:
            return None
    
    # ==================== 全球股指数据源 ====================
    
    def get_indices_from_sina(self):
        """新浪财经全球指数 - 数据源1"""
        indices = {}
        
        # 新浪全球指数代码映射
        sina_codes = {
            # A股指数
            "s_sh000001": {"name": "上证指数", "region": "中国大陆"},
            "s_sz399001": {"name": "深证成指", "region": "中国大陆"},
            "s_sz399006": {"name": "创业板指", "region": "中国大陆"},
            # 港股
            "rt_hkHSI": {"name": "恒生指数", "region": "中国香港"},
            "rt_hkHSCEI": {"name": "国企指数", "region": "中国香港"},
            "rt_hkHSTECH": {"name": "恒生科技", "region": "中国香港"},
            # 美股
            "gb_$dji": {"name": "道琼斯", "region": "美国"},
            "gb_$ixic": {"name": "纳斯达克", "region": "美国"},
            "gb_$inx": {"name": "标普500", "region": "美国"},
            # 欧洲
            "gb_$ftse": {"name": "富时100", "region": "英国"},
            "gb_$dax": {"name": "德国DAX", "region": "德国"},
            "gb_$cac": {"name": "法国CAC40", "region": "法国"},
            # 亚太
            "gb_$nikk": {"name": "日经225", "region": "日本"},
            "gb_$kospi": {"name": "韩国综合", "region": "韩国"},
            "gb_$twii": {"name": "台湾加权", "region": "中国台湾"},
            "gb_$sensex": {"name": "印度SENSEX", "region": "印度"},
            "gb_$asx": {"name": "澳洲标普200", "region": "澳大利亚"},
        }
        
        try:
            # A股指数
            a_codes = "s_sh000001,s_sz399001,s_sz399006"
            url = f"https://hq.sinajs.cn/list={a_codes}"
            headers = {'Referer': 'https://finance.sina.com.cn'}
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            resp.encoding = 'gbk'
            
            for line in resp.text.strip().split('\n'):
                if '=' in line:
                    code = line.split('=')[0].split('_')[-1]
                    full_code = f"s_{code}"
                    data_str = line.split('"')[1] if '"' in line else ""
                    if data_str and full_code in sina_codes:
                        parts = data_str.split(',')
                        if len(parts) >= 4:
                            info = sina_codes[full_code]
                            indices[info["name"]] = {
                                "name": info["name"],
                                "region": info["region"],
                                "price": float(parts[1]) if parts[1] else 0,
                                "change_amt": float(parts[2]) if parts[2] else 0,
                                "change_pct": float(parts[3]) if parts[3] else 0,
                                "source": "新浪"
                            }
            
            # 港股指数
            hk_codes = "rt_hkHSI,rt_hkHSCEI,rt_hkHSTECH"
            url = f"https://hq.sinajs.cn/list={hk_codes}"
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            resp.encoding = 'gbk'
            
            for line in resp.text.strip().split('\n'):
                if '=' in line and 'rt_hk' in line:
                    code = line.split('var hq_str_')[1].split('=')[0] if 'var hq_str_' in line else ""
                    data_str = line.split('"')[1] if '"' in line else ""
                    if data_str and code in sina_codes:
                        parts = data_str.split(',')
                        if len(parts) >= 9:
                            info = sina_codes[code]
                            price = float(parts[6]) if parts[6] else 0
                            prev_close = float(parts[3]) if parts[3] else price
                            change_amt = price - prev_close
                            change_pct = (change_amt / prev_close * 100) if prev_close else 0
                            indices[info["name"]] = {
                                "name": info["name"],
                                "region": info["region"],
                                "price": price,
                                "change_amt": change_amt,
                                "change_pct": change_pct,
                                "source": "新浪"
                            }
            
            # 全球指数
            global_codes = "gb_$dji,gb_$ixic,gb_$inx,gb_$ftse,gb_$dax,gb_$cac,gb_$nikk,gb_$kospi,gb_$twii,gb_$sensex,gb_$asx"
            url = f"https://hq.sinajs.cn/list={global_codes}"
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            resp.encoding = 'gbk'
            
            for line in resp.text.strip().split('\n'):
                if '=' in line:
                    for code, info in sina_codes.items():
                        if code.startswith('gb_') and code.split('gb_')[1] in line:
                            data_str = line.split('"')[1] if '"' in line else ""
                            if data_str:
                                parts = data_str.split(',')
                                if len(parts) >= 2:
                                    price = float(parts[1]) if parts[1] else 0
                                    prev_close = float(parts[26]) if len(parts) > 26 and parts[26] else price
                                    change_amt = price - prev_close
                                    change_pct = (change_amt / prev_close * 100) if prev_close else 0
                                    indices[info["name"]] = {
                                        "name": info["name"],
                                        "region": info["region"],
                                        "price": price,
                                        "change_amt": change_amt,
                                        "change_pct": change_pct,
                                        "source": "新浪"
                                    }
                            break
        except Exception as e:
            pass
        
        return indices
    
    def get_indices_from_eastmoney(self):
        """东方财富全球指数 - 数据源2"""
        indices = {}
        
        em_codes = [
            {"code": "1.000001", "name": "上证指数", "region": "中国大陆"},
            {"code": "0.399001", "name": "深证成指", "region": "中国大陆"},
            {"code": "0.399006", "name": "创业板指", "region": "中国大陆"},
            {"code": "100.HSI", "name": "恒生指数", "region": "中国香港"},
            {"code": "100.HSCEI", "name": "国企指数", "region": "中国香港"},
            {"code": "100.HSTECH", "name": "恒生科技", "region": "中国香港"},
            {"code": "100.DJIA", "name": "道琼斯", "region": "美国"},
            {"code": "100.NDX", "name": "纳斯达克", "region": "美国"},
            {"code": "100.SPX", "name": "标普500", "region": "美国"},
            {"code": "100.FTSE", "name": "富时100", "region": "英国"},
            {"code": "100.GDAXI", "name": "德国DAX", "region": "德国"},
            {"code": "100.FCHI", "name": "法国CAC40", "region": "法国"},
            {"code": "100.N225", "name": "日经225", "region": "日本"},
            {"code": "100.KS11", "name": "韩国综合", "region": "韩国"},
            {"code": "100.TWII", "name": "台湾加权", "region": "中国台湾"},
            {"code": "100.SENSEX", "name": "印度SENSEX", "region": "印度"},
            {"code": "100.AS51", "name": "澳洲标普200", "region": "澳大利亚"},
        ]
        
        def fetch_single(item):
            try:
                url = "https://push2.eastmoney.com/api/qt/stock/get"
                params = {
                    "secid": item["code"],
                    "fields": "f43,f44,f45,f46,f60,f169,f170",
                    "ut": "fa5fd1943c7b386f172d6893dbfba10b"
                }
                resp = self.session.get(url, params=params, timeout=5)
                data = resp.json().get("data", {})
                
                if data and data.get("f43"):
                    return {
                        "name": item["name"],
                        "region": item["region"],
                        "price": data.get("f43", 0) / 100,
                        "change_amt": data.get("f169", 0) / 100 if data.get("f169") else 0,
                        "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0,
                        "source": "东财"
                    }
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch_single, item): item for item in em_codes}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    indices[result["name"]] = result
        
        return indices
    
    def get_indices_from_tencent(self):
        """腾讯财经全球指数 - 数据源3"""
        indices = {}
        
        qq_codes = {
            "sh000001": {"name": "上证指数", "region": "中国大陆"},
            "sz399001": {"name": "深证成指", "region": "中国大陆"},
            "sz399006": {"name": "创业板指", "region": "中国大陆"},
            "hkHSI": {"name": "恒生指数", "region": "中国香港"},
            "hkHSCEI": {"name": "国企指数", "region": "中国香港"},
            "hkHSTECH": {"name": "恒生科技", "region": "中国香港"},
            "usNDX": {"name": "纳斯达克", "region": "美国"},
            "usDJI": {"name": "道琼斯", "region": "美国"},
            "usINX": {"name": "标普500", "region": "美国"},
        }
        
        try:
            codes_str = ",".join(qq_codes.keys())
            url = f"https://qt.gtimg.cn/q={codes_str}"
            resp = self.session.get(url, timeout=self.timeout)
            resp.encoding = 'gbk'
            
            for line in resp.text.strip().split(';'):
                if '=' not in line:
                    continue
                for code, info in qq_codes.items():
                    if f'v_{code}' in line:
                        data_str = line.split('"')[1] if '"' in line else ""
                        if data_str:
                            parts = data_str.split('~')
                            if len(parts) >= 40:
                                indices[info["name"]] = {
                                    "name": info["name"],
                                    "region": info["region"],
                                    "price": float(parts[3]) if parts[3] else 0,
                                    "change_amt": float(parts[31]) if parts[31] else 0,
                                    "change_pct": float(parts[32]) if parts[32] else 0,
                                    "source": "腾讯"
                                }
                        break
        except:
            pass
        
        return indices
    
    def get_all_indices(self):
        """聚合所有数据源，智能择优"""
        all_indices = {}
        
        # 并行获取所有数据源
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.get_indices_from_sina): "sina",
                executor.submit(self.get_indices_from_eastmoney): "eastmoney",
                executor.submit(self.get_indices_from_tencent): "tencent",
            }
            
            source_data = {}
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    result = future.result()
                    if result:
                        source_data[source_name] = result
                except:
                    pass
        
        # 定义需要展示的指数（按优先级排序的数据源）
        target_indices = [
            {"name": "上证指数", "region": "中国大陆", "priority": ["sina", "eastmoney", "tencent"]},
            {"name": "深证成指", "region": "中国大陆", "priority": ["sina", "eastmoney", "tencent"]},
            {"name": "创业板指", "region": "中国大陆", "priority": ["sina", "eastmoney", "tencent"]},
            {"name": "恒生指数", "region": "中国香港", "priority": ["sina", "eastmoney", "tencent"]},
            {"name": "恒生科技", "region": "中国香港", "priority": ["sina", "eastmoney", "tencent"]},
            {"name": "国企指数", "region": "中国香港", "priority": ["sina", "eastmoney", "tencent"]},
            {"name": "道琼斯", "region": "美国", "priority": ["sina", "eastmoney", "tencent"]},
            {"name": "纳斯达克", "region": "美国", "priority": ["sina", "eastmoney", "tencent"]},
            {"name": "标普500", "region": "美国", "priority": ["sina", "eastmoney", "tencent"]},
            {"name": "日经225", "region": "日本", "priority": ["sina", "eastmoney"]},
            {"name": "韩国综合", "region": "韩国", "priority": ["sina", "eastmoney"]},
            {"name": "台湾加权", "region": "中国台湾", "priority": ["sina", "eastmoney"]},
            {"name": "富时100", "region": "英国", "priority": ["sina", "eastmoney"]},
            {"name": "德国DAX", "region": "德国", "priority": ["sina", "eastmoney"]},
            {"name": "法国CAC40", "region": "法国", "priority": ["sina", "eastmoney"]},
            {"name": "印度SENSEX", "region": "印度", "priority": ["sina", "eastmoney"]},
        ]
        
        # 智能选择最佳数据源
        for idx_info in target_indices:
            name = idx_info["name"]
            for source in idx_info["priority"]:
                if source in source_data and name in source_data[source]:
                    data = source_data[source][name]
                    if data["price"] > 0:  # 数据有效性校验
                        all_indices[name] = data
                        break
            
            # 如果所有数据源都没有数据，添加占位
            if name not in all_indices:
                all_indices[name] = {
                    "name": name,
                    "region": idx_info["region"],
                    "price": 0,
                    "change_amt": 0,
                    "change_pct": 0,
                    "source": "暂无"
                }
        
        return list(all_indices.values())
    
    # ==================== 期货数据 ====================
    
    def get_futures_data(self):
        """获取期货数据 - 多源"""
        futures = []
        
        # 东方财富期货
        em_futures = [
            {"code": "113.IH00", "name": "上证50期货", "type": "股指", "divisor": 100},
            {"code": "113.IF00", "name": "沪深300期货", "type": "股指", "divisor": 100},
            {"code": "113.IC00", "name": "中证500期货", "type": "股指", "divisor": 100},
            {"code": "113.IM00", "name": "中证1000期货", "type": "股指", "divisor": 100},
            {"code": "113.AU0", "name": "沪金主力", "type": "贵金属", "divisor": 1},
            {"code": "113.AG0", "name": "沪银主力", "type": "贵金属", "divisor": 1},
            {"code": "113.SC0", "name": "原油主力", "type": "能源", "divisor": 1},
            {"code": "113.FU0", "name": "燃油主力", "type": "能源", "divisor": 1},
            {"code": "113.CU0", "name": "沪铜主力", "type": "有色", "divisor": 1},
            {"code": "113.AL0", "name": "沪铝主力", "type": "有色", "divisor": 1},
            {"code": "113.ZN0", "name": "沪锌主力", "type": "有色", "divisor": 1},
            {"code": "113.NI0", "name": "沪镍主力", "type": "有色", "divisor": 1},
        ]
        
        def fetch_future(item):
            try:
                url = "https://push2.eastmoney.com/api/qt/stock/get"
                params = {
                    "secid": item["code"],
                    "fields": "f43,f44,f45,f46,f60,f169,f170",
                    "ut": "fa5fd1943c7b386f172d6893dbfba10b"
                }
                resp = self.session.get(url, params=params, timeout=5)
                data = resp.json().get("data", {})
                
                if data and data.get("f43"):
                    price = data.get("f43", 0) / item["divisor"]
                    return {
                        "name": item["name"],
                        "type": item["type"],
                        "price": price,
                        "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0,
                    }
            except:
                pass
            return {"name": item["name"], "type": item["type"], "price": 0, "change_pct": 0}
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(fetch_future, em_futures))
            futures = [r for r in results if r]
        
        return futures
    
    # ==================== 外汇数据 ====================
    
    def get_forex_data(self):
        """获取外汇数据"""
        forex = []
        
        forex_codes = [
            {"code": "USDCNY", "name": "美元/人民币", "sina_code": "USDCNY"},
            {"code": "EURCNY", "name": "欧元/人民币", "sina_code": "EURCNY"},
            {"code": "JPYCNY", "name": "日元/人民币", "sina_code": "JPYCNY"},
            {"code": "GBPCNY", "name": "英镑/人民币", "sina_code": "GBPCNY"},
            {"code": "HKDCNY", "name": "港币/人民币", "sina_code": "HKDCNY"},
        ]
        
        try:
            codes = ",".join([f"fx_s{c['sina_code']}" for c in forex_codes])
            url = f"https://hq.sinajs.cn/list={codes}"
            headers = {'Referer': 'https://finance.sina.com.cn'}
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            resp.encoding = 'gbk'
            
            for line in resp.text.strip().split('\n'):
                if '=' in line and '"' in line:
                    data_str = line.split('"')[1]
                    if data_str:
                        parts = data_str.split(',')
                        if len(parts) >= 8:
                            for fc in forex_codes:
                                if fc["sina_code"] in line:
                                    current = float(parts[1]) if parts[1] else 0
                                    prev = float(parts[3]) if parts[3] else current
                                    change_pct = ((current - prev) / prev * 100) if prev else 0
                                    forex.append({
                                        "name": fc["name"],
                                        "price": current,
                                        "change_pct": change_pct
                                    })
                                    break
        except:
            pass
        
        return forex

# ==================== 新闻数据模块 ====================

class NewsAggregator:
    """新闻聚合器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_news_from_eastmoney(self):
        """东方财富新闻"""
        news = {"politics": [], "economy": [], "tech": []}
        
        try:
            url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
            
            # 财经要闻
            for col_id, category in [("350", "economy"), ("345", "politics"), ("351", "tech")]:
                params = {"columns": col_id, "pageSize": 15, "pageIndex": 0, "type": 1}
                resp = self.session.get(url, params=params, timeout=10)
                data = resp.json()
                
                if data.get("data"):
                    for item in data["data"][:15]:
                        news[category].append({
                            "title": item.get("title", ""),
                            "time": item.get("showTime", ""),
                            "source": item.get("mediaName", "东方财富"),
                            "url": item.get("url", "")
                        })
        except:
            pass
        
        return news
    
    def get_news_from_sina(self):
        """新浪财经新闻"""
        news = {"politics": [], "economy": [], "tech": []}
        
        try:
            url = "https://feed.mix.sina.com.cn/api/roll/get"
            params = {"pageid": "153", "lid": "2516", "num": 50, "page": 1}
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            
            if data.get("result", {}).get("data"):
                for item in data["result"]["data"]:
                    title = item.get("title", "")
                    news_item = {
                        "title": title,
                        "time": datetime.fromtimestamp(int(item.get("ctime", 0))).strftime("%H:%M") if item.get("ctime") else "",
                        "source": item.get("media_name", "新浪财经"),
                        "url": item.get("url", "")
                    }
                    
                    # 智能分类
                    if any(kw in title for kw in ["政策", "央行", "两会", "国务院", "发改委", "政府", "关税", "制裁", "外交", "领导人", "会议", "总书记"]):
                        if len(news["politics"]) < 15:
                            news["politics"].append(news_item)
                    elif any(kw in title for kw in ["AI", "人工智能", "芯片", "半导体", "机器人", "DeepSeek", "科技", "技术", "算力", "大模型", "ChatGPT", "英伟达", "数据中心"]):
                        if len(news["tech"]) < 15:
                            news["tech"].append(news_item)
                    else:
                        if len(news["economy"]) < 15:
                            news["economy"].append(news_item)
        except:
            pass
        
        return news
    
    def get_news_from_cls(self):
        """财联社电报"""
        news = {"politics": [], "economy": [], "tech": []}
        
        try:
            url = "https://www.cls.cn/nodeapi/updateTelegraphList"
            params = {"app": "CailianpressWeb", "os": "web", "sv": "7.7.5"}
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            
            if data.get("data", {}).get("roll_data"):
                for item in data["data"]["roll_data"][:50]:
                    title = item.get("title", "") or item.get("content", "")[:60]
                    if not title:
                        continue
                    
                    news_item = {
                        "title": title,
                        "time": datetime.fromtimestamp(item.get("ctime", 0)).strftime("%H:%M") if item.get("ctime") else "",
                        "source": "财联社",
                        "url": ""
                    }
                    
                    if any(kw in title for kw in ["政策", "央行", "政府", "部委", "会议"]):
                        if len(news["politics"]) < 15:
                            news["politics"].append(news_item)
                    elif any(kw in title for kw in ["AI", "芯片", "科技", "算力", "机器人"]):
                        if len(news["tech"]) < 15:
                            news["tech"].append(news_item)
                    else:
                        if len(news["economy"]) < 15:
                            news["economy"].append(news_item)
        except:
            pass
        
        return news
    
    def get_all_news(self):
        """聚合所有新闻源"""
        all_news = {"politics": [], "economy": [], "tech": []}
        
        # 并行获取
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.get_news_from_eastmoney),
                executor.submit(self.get_news_from_sina),
                executor.submit(self.get_news_from_cls),
            ]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    for category in ["politics", "economy", "tech"]:
                        all_news[category].extend(result.get(category, []))
                except:
                    pass
        
        # 去重并限制数量
        for category in all_news:
            seen_titles = set()
            unique_news = []
            for item in all_news[category]:
                # 简单去重：取标题前20字符
                key = item["title"][:20]
                if key not in seen_titles:
                    seen_titles.add(key)
                    unique_news.append(item)
            all_news[category] = unique_news[:10]
        
        return all_news

# ==================== A股数据模块 ====================

class AStockData:
    """A股数据"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @st.cache_data(ttl=60)
    def get_stock_list(_self):
        """获取A股列表"""
        stocks = []
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            
            for fs in ["m:1+t:2,m:1+t:23", "m:0+t:6,m:0+t:80"]:
                market = "sh" if "m:1" in fs else "sz"
                params = {
                    "pn": 1, "pz": 3000, "fs": fs,
                    "fields": "f12,f14", "ut": "fa5fd1943c7b386f172d6893dbfba10b"
                }
                resp = _self.session.get(url, params=params, timeout=10)
                for item in resp.json().get("data", {}).get("diff", []):
                    stocks.append({"code": item["f12"], "name": item["f14"], "market": market})
        except:
            pass
        return stocks
    
    def get_stock_realtime(self, code, market):
        """获取股票实时数据"""
        try:
            secid = f"1.{code}" if market == "sh" else f"0.{code}"
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": secid,
                "fields": "f43,f44,f45,f46,f47,f48,f50,f57,f58,f60,f169,f170,f171",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            resp = self.session.get(url, params=params, timeout=5)
            data = resp.json().get("data", {})
            
            if data:
                return {
                    "code": code,
                    "name": data.get("f58", ""),
                    "price": data.get("f43", 0) / 100 if data.get("f43") else 0,
                    "change_pct": data.get("f170", 0) / 100 if data.get("f170") else 0,
                    "change_amt": data.get("f169", 0) / 100 if data.get("f169") else 0,
                    "volume": data.get("f47", 0) / 10000 if data.get("f47") else 0,
                    "amount": data.get("f48", 0) / 100000000 if data.get("f48") else 0,
                    "turnover": data.get("f50", 0) / 100 if data.get("f50") else 0,
                    "high": data.get("f44", 0) / 100 if data.get("f44") else 0,
                    "low": data.get("f45", 0) / 100 if data.get("f45") else 0,
                    "open": data.get("f46", 0) / 100 if data.get("f46") else 0,
                    "prev_close": data.get("f60", 0) / 100 if data.get("f60") else 0,
                }
        except:
            pass
        return None

# ==================== 数据缓存包装 ====================

@st.cache_data(ttl=120)
def fetch_global_indices():
    return GlobalMarketData().get_all_indices()

@st.cache_data(ttl=120)
def fetch_futures_data():
    return GlobalMarketData().get_futures_data()

@st.cache_data(ttl=120)
def fetch_forex_data():
    return GlobalMarketData().get_forex_data()

@st.cache_data(ttl=300)
def fetch_news_data():
    return NewsAggregator().get_all_news()

@st.cache_data(ttl=60)
def fetch_stock_list():
    return AStockData().get_stock_list()

def get_stock_data(code, market):
    return AStockData().get_stock_realtime(code, market)

# ==================== 会话状态 ====================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = {}
if "alerts" not in st.session_state:
    st.session_state.alerts = {}
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "global"

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px 0;'>
        <div style='font-size: 24px; font-weight: 700; color: #f5f5f7;'>📊 股市观察</div>
        <div style='font-size: 13px; color: #86868b; margin-top: 4px;'>全球行情与资讯</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 10px 0;'></div>", unsafe_allow_html=True)
    
    tab = st.radio("功能模块", ["🌍 全球行情", "📈 A股监控"], label_visibility="collapsed")
    st.session_state.current_tab = "global" if "全球" in tab else "a_stock"
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    if st.session_state.current_tab == "a_stock":
        st.markdown("<div style='font-size: 15px; font-weight: 600; color: #f5f5f7; margin-bottom: 12px;'>搜索股票</div>", unsafe_allow_html=True)
        search = st.text_input("", placeholder="输入代码或名称", label_visibility="collapsed")
        
        if search:
            stocks = fetch_stock_list()
            results = [s for s in stocks if search.lower() in s["code"].lower() or search in s["name"]][:8]
            
            for stock in results:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"<div style='color: #f5f5f7; font-size: 14px;'>{stock['name']} <span style='color: #86868b;'>{stock['code']}</span></div>", unsafe_allow_html=True)
                with col2:
                    if st.button("＋", key=f"add_{stock['code']}"):
                        st.session_state.watchlist[stock["code"]] = {"name": stock["name"], "market": stock["market"]}
                        st.rerun()
        
        st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 20px 0;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 15px; font-weight: 600; color: #f5f5f7; margin-bottom: 12px;'>监控列表</div>", unsafe_allow_html=True)
        
        if st.session_state.watchlist:
            for code, info in list(st.session_state.watchlist.items()):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"<div style='color: #f5f5f7; font-size: 14px;'>{info['name']}</div>", unsafe_allow_html=True)
                with col2:
                    if st.button("✕", key=f"del_{code}"):
                        del st.session_state.watchlist[code]
                        st.rerun()
        else:
            st.markdown("<div style='color: #86868b; font-size: 13px;'>暂无监控</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1px; background: #2c2c2e; margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    if st.button("刷新数据", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown(f"<div style='color: #48484a; font-size: 11px; margin-top: 20px; text-align: center;'>{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>", unsafe_allow_html=True)

# ==================== 主界面 ====================

if st.session_state.current_tab == "global":
    st.markdown("""
    <div class='main-title'>股市观察</div>
    <div class='sub-title'>全球市场实时行情 · 财经资讯一览</div>
    """, unsafe_allow_html=True)
    
    # 获取数据
    with st.spinner("正在获取全球行情数据..."):
        indices = fetch_global_indices()
        futures = fetch_futures_data()
        forex = fetch_forex_data()
        news = fetch_news_data()
    
    # ========== 全球股指 ==========
    st.markdown("<div class='section-header'>全球股指</div>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    for i, idx in enumerate(indices):
        with cols[i % 4]:
            change_class = "up" if idx["change_pct"] > 0 else ("down" if idx["change_pct"] < 0 else "neutral")
            change_symbol = "+" if idx["change_pct"] > 0 else ""
            
            st.markdown(f"""
            <div class='index-card'>
                <div class='index-region'>{idx['region']}</div>
                <div class='index-name'>{idx['name']}</div>
                <div class='index-price'>{idx['price']:,.2f}</div>
                <div class='index-change {change_class}'>{change_symbol}{idx['change_pct']:.2f}%</div>
                <div class='data-source'>数据源: {idx.get('source', '-')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== 期货 & 外汇 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='section-header'>期货行情</div>", unsafe_allow_html=True)
        fut_cols = st.columns(3)
        for i, fut in enumerate(futures[:9]):
            with fut_cols[i % 3]:
                change_class = "up" if fut["change_pct"] > 0 else ("down" if fut["change_pct"] < 0 else "neutral")
                change_symbol = "+" if fut["change_pct"] > 0 else ""
                st.markdown(f"""
                <div class='futures-card'>
                    <div class='futures-name'>{fut['name']}</div>
                    <div class='futures-price'>{fut['price']:,.2f}</div>
                    <div class='futures-change {change_class}'>{change_symbol}{fut['change_pct']:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='section-header'>外汇牌价</div>", unsafe_allow_html=True)
        if forex:
            fx_cols = st.columns(3)
            for i, fx in enumerate(forex[:6]):
                with fx_cols[i % 3]:
                    change_class = "up" if fx["change_pct"] > 0 else ("down" if fx["change_pct"] < 0 else "neutral")
                    change_symbol = "+" if fx["change_pct"] > 0 else ""
                    st.markdown(f"""
                    <div class='futures-card'>
                        <div class='futures-name'>{fx['name']}</div>
                        <div class='futures-price'>{fx['price']:.4f}</div>
                        <div class='futures-change {change_class}'>{change_symbol}{fx['change_pct']:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # ========== 财经资讯 ==========
    st.markdown("<div class='section-header'>财经资讯</div>", unsafe_allow_html=True)
    
    news_cols = st.columns(3)
    
    categories = [
        ("politics", "🏛️ 政治要闻", "tag-politics"),
        ("economy", "💰 经济要闻", "tag-economy"),
        ("tech", "🔬 科技要闻", "tag-tech"),
    ]
    
    for col, (cat_key, cat_name, tag_class) in zip(news_cols, categories):
        with col:
            st.markdown(f"<div class='news-section-title'>{cat_name}</div>", unsafe_allow_html=True)
            for i, item in enumerate(news.get(cat_key, [])[:10], 1):
                title = item['title'][:45] + '...' if len(item['title']) > 45 else item['title']
                st.markdown(f"""
                <div class='news-card'>
                    <div class='news-number'>{i:02d}</div>
                    <div class='news-title'>{title}</div>
                    <div class='news-meta'>
                        <span class='tag {tag_class}'>{cat_name[2:]}</span>
                        {item.get('time', '')} · {item.get('source', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='footer-info'>
        数据更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        数据来源: 新浪财经 / 东方财富 / 腾讯财经 / 财联社 · 多源聚合智能择优
    </div>
    """, unsafe_allow_html=True)

else:
    # A股监控页面
    st.markdown("""
    <div class='main-title'>股市观察</div>
    <div class='sub-title'>A股实时监控 · 智能预警</div>
    """, unsafe_allow_html=True)
    
    now = datetime.now()
    is_trading = now.weekday() < 5 and ((9 <= now.hour < 11) or (now.hour == 11 and now.minute <= 30) or (13 <= now.hour < 15))
    
    if not is_trading:
        st.markdown("""
        <div style='background: rgba(255, 159, 10, 0.1); border: 1px solid rgba(255, 159, 10, 0.3); border-radius: 12px; padding: 16px; margin-bottom: 24px;'>
            <span style='color: #ff9f0a; font-size: 14px;'>⏰ 非交易时段，显示最近收盘数据</span>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.watchlist:
        cols = st.columns(3)
        
        for i, (code, info) in enumerate(st.session_state.watchlist.items()):
            data = get_stock_data(code, info["market"])
            
            if data:
                with cols[i % 3]:
                    change_class = "up" if data["change_pct"] > 0 else ("down" if data["change_pct"] < 0 else "neutral")
                    change_symbol = "+" if data["change_pct"] > 0 else ""
                    
                    st.markdown(f"""
                    <div class='stock-card'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div class='stock-name'>{data['name']}</div>
                            <div class='stock-code'>{data['code']}</div>
                        </div>
                        <div class='stock-price {change_class}'>¥{data['price']:.2f}</div>
                        <div class='index-change {change_class}' style='margin-bottom: 16px;'>
                            {change_symbol}{data['change_amt']:.2f} ({change_symbol}{data['change_pct']:.2f}%)
                        </div>
                        <div class='stock-detail'>
                            <span class='detail-label'>成交量</span>
                            <span class='detail-value'>{data['volume']:.2f} 万手</span>
                        </div>
                        <div class='stock-detail'>
                            <span class='detail-label'>成交额</span>
                            <span class='detail-value'>{data['amount']:.2f} 亿</span>
                        </div>
                        <div class='stock-detail'>
                            <span class='detail-label'>换手率</span>
                            <span class='detail-value'>{data['turnover']:.2f}%</span>
                        </div>
                        <div class='stock-detail'>
                            <span class='detail-label'>最高 / 最低</span>
                            <span class='detail-value'>{data['high']:.2f} / {data['low']:.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("报警设置"):
                        if code not in st.session_state.alerts:
                            st.session_state.alerts[code] = {"price_low": 0, "price_high": 0, "change_low": -10, "change_high": 10}
                        
                        alert = st.session_state.alerts[code]
                        c1, c2 = st.columns(2)
                        with c1:
                            alert["price_low"] = st.number_input("价格下限", value=alert["price_low"], step=0.1, key=f"pl_{code}")
                        with c2:
                            alert["price_high"] = st.number_input("价格上限", value=alert["price_high"], step=0.1, key=f"ph_{code}")
    else:
        st.markdown("""
        <div class='empty-state'>
            <div class='empty-state-icon'>📈</div>
            <div class='empty-state-text'>在左侧搜索添加股票开始监控</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>热门股票</div>", unsafe_allow_html=True)
        
        hot_stocks = [
            {"code": "301165", "name": "锐捷网络", "market": "sz"},
            {"code": "300750", "name": "宁德时代", "market": "sz"},
            {"code": "600519", "name": "贵州茅台", "market": "sh"},
            {"code": "000858", "name": "五粮液", "market": "sz"},
            {"code": "002475", "name": "立讯精密", "market": "sz"},
            {"code": "300059", "name": "东方财富", "market": "sz"},
        ]
        
        cols = st.columns(3)
        for i, stock in enumerate(hot_stocks):
            with cols[i % 3]:
                if st.button(f"＋ {stock['name']}", key=f"hot_{stock['code']}", use_container_width=True):
                    st.session_state.watchlist[stock["code"]] = {"name": stock["name"], "market": stock["market"]}
                    st.rerun()
    
    st.markdown(f"<div class='timestamp'>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)
