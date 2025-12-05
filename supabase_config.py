"""
Supabase 配置和工具函数
用于替代本地文件存储
"""
import os
from supabase import create_client, Client
from typing import List, Dict, Optional
import base64
from io import BytesIO
from PIL import Image

# 从环境变量获取Supabase配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = "journal-images"  # Storage bucket名称

def get_supabase_client() -> Optional[Client]:
    """获取Supabase客户端"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase客户端创建失败: {e}")
        return None

def upload_image_to_supabase(image: Image.Image, filename: str, folder: str = "journals") -> Optional[str]:
    """
    上传图片到Supabase Storage
    
    Args:
        image: PIL Image对象
        filename: 文件名
        folder: 存储文件夹（默认为journals）
    
    Returns:
        图片的公开URL，失败返回None
    """
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        # 将PIL Image转换为bytes
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        
        # 构建存储路径
        storage_path = f"{folder}/{filename}"
        
        # 上传到Supabase Storage
        response = client.storage.from_(SUPABASE_BUCKET).upload(
            path=storage_path,
            file=image_bytes,
            file_options={"content-type": "image/png", "upsert": "true"}
        )
        
        # 获取公开URL
        public_url = client.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
        return public_url
        
    except Exception as e:
        print(f"图片上传失败: {e}")
        return None

def upload_file_to_supabase(file_bytes: bytes, filename: str, folder: str = "uploads") -> Optional[str]:
    """
    上传文件到Supabase Storage（用于用户上传的原始图片）
    
    Args:
        file_bytes: 文件字节数据
        filename: 文件名
        folder: 存储文件夹
    
    Returns:
        图片的公开URL，失败返回None
    """
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        storage_path = f"{folder}/{filename}"
        
        # 根据文件扩展名确定content-type
        content_type = "image/jpeg"
        if filename.lower().endswith(".png"):
            content_type = "image/png"
        
        response = client.storage.from_(SUPABASE_BUCKET).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        
        public_url = client.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
        return public_url
        
    except Exception as e:
        print(f"文件上传失败: {e}")
        return None

def load_journals_from_supabase() -> List[Dict]:
    """从Supabase加载所有日记条目"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        response = client.table("journals").select("*").order("created_at", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"加载日记失败: {e}")
        return []

def save_journal_to_supabase(journal_data: Dict) -> Optional[str]:
    """
    保存日记条目到Supabase
    
    Args:
        journal_data: 包含 date, weather, text, image_paths, journal_image_url 的字典
    
    Returns:
        创建的记录ID，失败返回None
    """
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.table("journals").insert(journal_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
        return None
    except Exception as e:
        print(f"保存日记失败: {e}")
        return None

def update_journal_in_supabase(journal_id: str, journal_data: Dict) -> bool:
    """更新日记条目"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        response = client.table("journals").update(journal_data).eq("id", journal_id).execute()
        return True
    except Exception as e:
        print(f"更新日记失败: {e}")
        return False

def delete_journal_from_supabase(journal_id: str) -> bool:
    """删除日记条目"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        # 注意：这里只删除数据库记录，不删除Storage中的图片
        # 如果需要同时删除图片，需要额外调用Storage API
        response = client.table("journals").delete().eq("id", journal_id).execute()
        return True
    except Exception as e:
        print(f"删除日记失败: {e}")
        return False

def search_journals_in_supabase(query: str) -> List[Dict]:
    """搜索日记（按日期、天气或文字内容）"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        # 使用PostgreSQL的ILIKE进行模糊搜索
        # Supabase Python客户端使用不同的语法
        response = client.table("journals").select("*").or_(
            f"date.ilike.%{query}%,weather.ilike.%{query}%,text.ilike.%{query}%"
        ).order("created_at", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        # 如果or_语法不支持，使用多个查询然后合并
        try:
            results = []
            # 分别搜索每个字段
            for field in ["date", "weather", "text"]:
                field_response = client.table("journals").select("*").ilike(field, f"%{query}%").execute()
                if field_response.data:
                    results.extend(field_response.data)
            
            # 去重（基于id）
            seen_ids = set()
            unique_results = []
            for item in results:
                if item["id"] not in seen_ids:
                    seen_ids.add(item["id"])
                    unique_results.append(item)
            
            # 按创建时间排序
            unique_results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return unique_results
        except Exception as e2:
            print(f"搜索日记失败: {e2}")
            return []

def filter_journals_by_weather(weather: str) -> List[Dict]:
    """按天气筛选日记"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        if weather == "全部":
            return load_journals_from_supabase()
        response = client.table("journals").select("*").eq("weather", weather).order("created_at", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"筛选日记失败: {e}")
        return []

