"""
设置管理路由组件
提供WebUI的通用设置管理，如壁纸上传等
"""

import shutil
from pathlib import Path
from typing import Optional

from fastapi import UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.common.logger import get_logger
from src.common.security import VerifiedDep
from src.plugin_system import BaseRouterComponent
from src.config.config import PROJECT_ROOT

logger = get_logger("WebUI.SettingRouter")

# 数据目录
DATA_DIR = Path(PROJECT_ROOT) / "data" / "webui"
WALLPAPER_DIR = DATA_DIR

class WallpaperResponse(BaseModel):
    """壁纸上传响应"""
    success: bool
    url: str
    message: Optional[str] = None

class WebUISettingRouter(BaseRouterComponent):
    """
    WebUI设置管理路由组件
    
    提供以下API端点：
    - POST /wallpaper: 上传壁纸
    - GET /wallpaper: 获取当前壁纸
    - DELETE /wallpaper: 删除当前壁纸
    """
    
    component_name = "setting"
    component_description = "WebUI设置管理接口"
    
    def __init__(self):
        super().__init__()
        # 确保目录存在
        WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)
    
    def register_endpoints(self) -> None:
        """注册所有HTTP端点"""
        
        @self.router.post("/wallpaper", summary="上传壁纸", response_model=WallpaperResponse)
        async def upload_wallpaper(file: UploadFile = File(...), _=VerifiedDep):
            """
            上传WebUI壁纸
            """
            try:
                # 检查文件类型
                if not file.content_type.startswith("image/"):
                    raise HTTPException(status_code=400, detail="只能上传图片文件")
                
                # 保存文件
                # 使用固定名称 wallpaper.png (或保留扩展名)
                # 为了简单起见，我们统一转换为 png 或保留原扩展名
                # 这里我们简单地保存为 wallpaper_current
                
                ext = Path(file.filename).suffix
                if not ext:
                    ext = ".png"
                
                filename = f"current_wallpaper{ext}"
                file_path = WALLPAPER_DIR / filename
                
                # 删除旧的壁纸（如果有不同扩展名的）
                for old_file in WALLPAPER_DIR.glob("current_wallpaper*"):
                    try:
                        old_file.unlink()
                    except Exception:
                        pass
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # 返回访问URL
                # 注意：这里需要前端配合，或者我们提供一个获取图片的接口
                # 假设我们提供一个 GET /api/setting/wallpaper/image 接口
                
                return WallpaperResponse(
                    success=True,
                    url=f"/api/setting/wallpaper/image?t={int(file_path.stat().st_mtime)}",
                    message="壁纸上传成功"
                )
            
            except Exception as e:
                logger.error(f"上传壁纸失败: {e}")
                return WallpaperResponse(success=False, url="", message=str(e))

        @self.router.get("/wallpaper/image", summary="获取壁纸图片")
        async def get_wallpaper_image():
            """
            获取当前壁纸图片文件
            """
            try:
                # 查找当前壁纸
                files = list(WALLPAPER_DIR.glob("current_wallpaper*"))
                if not files:
                    raise HTTPException(status_code=404, detail="未设置壁纸")
                
                return FileResponse(files[0])
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"获取壁纸失败: {e}")
                raise HTTPException(status_code=500, detail="获取壁纸失败")

        @self.router.delete("/wallpaper", summary="删除壁纸")
        async def delete_wallpaper(_=VerifiedDep):
            """
            删除当前壁纸
            """
            try:
                files = list(WALLPAPER_DIR.glob("current_wallpaper*"))
                for f in files:
                    f.unlink()
                
                return {"success": True, "message": "壁纸已删除"}
            except Exception as e:
                logger.error(f"删除壁纸失败: {e}")
                return {"success": False, "message": str(e)}
