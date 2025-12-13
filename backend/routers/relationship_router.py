"""
人物关系管理路由组件
提供用户关系查询和管理API接口
"""

from typing import Any, Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field

from src.common.logger import get_logger
from src.common.security import VerifiedDep
from src.plugin_system import BaseRouterComponent
from src.plugin_system.apis import person_api

logger = get_logger("WebUI.RelationshipRouter")


# ==================== 请求模型 ====================


class UpdateRelationshipRequest(BaseModel):
    """更新关系请求"""

    relationship_score: float = Field(..., ge=0.0, le=1.0, description="关系分数 (0.0 - 1.0)")
    relationship_text: Optional[str] = Field(None, description="关系描述文本")


class UpdateImpressionRequest(BaseModel):
    """更新印象请求"""

    impression: Optional[str] = Field(None, description="详细印象")
    short_impression: Optional[str] = Field(None, description="简短印象")


# ==================== 响应模型 ====================


class PersonBasicInfoResponse(BaseModel):
    """用户基础信息响应"""

    person_id: str
    person_name: str
    nickname: Optional[str] = None
    know_times: int = 0
    know_since: Optional[str] = None
    last_know: Optional[str] = None
    attitude: Optional[int] = None  # 修正: 态度值是整数类型


class PersonCardResponse(BaseModel):
    """用户卡片信息响应（列表展示用）"""

    person_id: str
    person_name: str
    nickname: Optional[str] = None
    relationship_score: float = 0.0
    relationship_text: Optional[str] = None
    short_impression: Optional[str] = None
    know_times: int = 0
    last_know: Optional[str] = None


class PersonRelationshipResponse(BaseModel):
    """用户关系响应"""

    person_id: str
    person_name: str
    relationship_score: float
    relationship_text: Optional[str] = None


class PersonDetailResponse(BaseModel):
    """用户详情响应"""

    basic_info: PersonBasicInfoResponse
    relationship: PersonRelationshipResponse
    impression: str
    short_impression: str
    memory_points: list[dict[str, Any]]


class PersonListResponse(BaseModel):
    """用户列表响应"""

    persons: list[PersonCardResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RelationshipReportResponse(BaseModel):
    """关系报告响应"""

    person_id: str
    report: str


class UpdateRelationshipResponse(BaseModel):
    """更新关系响应"""

    success: bool
    message: str


# ==================== 路由组件 ====================


class RelationshipRouterComponent(BaseRouterComponent):
    """
    人物关系管理路由组件
    
    提供以下API端点：
    - GET /relationship/person/{person_id}: 获取用户详情
    - PUT /relationship/person/{person_id}: 更新用户关系
    - GET /relationship/person/{person_id}/report: 获取关系报告
    - GET /relationship/search: 搜索用户
    - GET /relationship/stats: 获取关系统计
    - POST /relationship/cache/clear: 清理关系缓存
    """
    
    component_name = "relationship"
    component_description = "人物关系管理接口"
    
    def register_endpoints(self) -> None:
        """注册所有HTTP端点"""
        
        @self.router.get(
            "/list",
            response_model=PersonListResponse,
            summary="获取用户列表",
            description="获取所有用户的卡片信息，支持分页",
        )
        async def get_person_list(page: int = 1, page_size: int = 20, _=VerifiedDep):
            """获取用户列表"""
            try:
                from src.common.database.core.models import PersonInfo
                from src.common.database.core.session import get_db_session
                from sqlalchemy import select, func
                
                async with get_db_session() as session:
                    # 获取总数
                    count_stmt = select(func.count()).select_from(PersonInfo)
                    result = await session.execute(count_stmt)
                    total = result.scalar() or 0
                    
                    # 计算分页
                    total_pages = (total + page_size - 1) // page_size
                    offset = (page - 1) * page_size
                    
                    # 查询用户列表，按最后交互时间排序
                    stmt = (
                        select(PersonInfo)
                        .order_by(PersonInfo.last_know.desc())
                        .limit(page_size)
                        .offset(offset)
                    )
                    result = await session.execute(stmt)
                    persons_data = result.scalars().all()
                    
                    # 构建响应
                    persons = []
                    for person in persons_data:
                        person_id = person.person_id
                        
                        # 获取关系数据
                        try:
                            relationship_data = await person_api.get_user_relationship_data(person_id)
                            relationship_score = relationship_data.get("relationship_score", 0.0)
                            relationship_text = relationship_data.get("relationship_text")
                        except Exception:
                            relationship_score = 0.0
                            relationship_text = None
                        
                        # 获取简短印象
                        try:
                            short_impression = await person_api.get_person_impression(person_id, short=True)
                        except Exception:
                            short_impression = None
                        
                        persons.append(PersonCardResponse(
                            person_id=person_id,
                            person_name=person.person_name or "未知用户",
                            nickname=person.nickname,
                            relationship_score=relationship_score,
                            relationship_text=relationship_text,
                            short_impression=short_impression,
                            know_times=person.know_times or 0,
                            last_know=person.last_know
                        ))
                    
                    return PersonListResponse(
                        persons=persons,
                        total=total,
                        page=page,
                        page_size=page_size,
                        total_pages=total_pages
                    )
                    
            except Exception as e:
                logger.error(f"获取用户列表失败: {e}")
                return PersonListResponse(
                    persons=[],
                    total=0,
                    page=page,
                    page_size=page_size,
                    total_pages=0
                )
        
        @self.router.get(
            "/person/{person_id}",
            response_model=PersonDetailResponse,
            summary="获取用户详情",
            description="获取指定用户的完整信息，包括基础信息、关系数据、印象和记忆点",
        )
        async def get_person_detail(person_id: str, _=VerifiedDep):
            """获取用户详情"""
            try:
                # 获取基础信息
                basic_info = await person_api.get_person_info(person_id)
                if not basic_info:
                    raise HTTPException(status_code=404, detail="用户不存在")

                # 获取关系数据
                try:
                    relationship_data = await person_api.get_user_relationship_data(person_id)
                except Exception as e:
                    logger.warning(f"获取关系数据失败: {e}, 使用默认值")
                    relationship_data = {"relationship_score": 0.0, "relationship_text": None}

                # 获取印象
                try:
                    impression = await person_api.get_person_impression(person_id, short=False)
                except Exception as e:
                    logger.warning(f"获取完整印象失败: {e}, 使用默认值")
                    impression = "暂无印象"
                
                try:
                    short_impression = await person_api.get_person_impression(person_id, short=True)
                except Exception as e:
                    logger.warning(f"获取简短印象失败: {e}, 使用默认值")
                    short_impression = "暂无印象"

                # 获取记忆点
                try:
                    points = await person_api.get_person_points(person_id, limit=10)
                    memory_points = [{"content": p[0], "weight": p[1], "timestamp": str(p[2])} for p in points]
                except Exception as e:
                    logger.warning(f"获取记忆点失败: {e}, 使用空列表")
                    memory_points = []

                return PersonDetailResponse(
                    basic_info=PersonBasicInfoResponse(
                        person_id=person_id,
                        person_name=basic_info.get("person_name", "未知用户"),
                        nickname=basic_info.get("nickname"),
                        know_times=basic_info.get("know_times", 0),
                        know_since=basic_info.get("know_since"),
                        last_know=basic_info.get("last_know"),
                        attitude=basic_info.get("attitude")
                    ),
                    relationship=PersonRelationshipResponse(
                        person_id=person_id,
                        person_name=basic_info.get("person_name", "未知用户"),
                        relationship_score=relationship_data.get("relationship_score", 0.0),
                        relationship_text=relationship_data.get("relationship_text")
                    ),
                    impression=impression,
                    short_impression=short_impression,
                    memory_points=memory_points,
                )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"获取用户详情失败: {e}")
                raise HTTPException(status_code=500, detail=f"获取用户详情失败: {str(e)}")

        @self.router.put(
            "/person/{person_id}",
            response_model=UpdateRelationshipResponse,
            summary="更新用户关系",
            description="更新指定用户的关系分数和关系描述",
        )
        async def update_person_relationship(person_id: str, request: UpdateRelationshipRequest, _=VerifiedDep):
            """更新用户关系"""
            try:
                # 获取用户名
                basic_info = await person_api.get_person_info(person_id)
                if not basic_info:
                    return UpdateRelationshipResponse(success=False, message="用户不存在")

                user_name = basic_info.get("person_name", "")

                # 更新关系
                await person_api.update_user_relationship(user_id=person_id, relationship_score=request.relationship_score, relationship_text=request.relationship_text, user_name=user_name)

                return UpdateRelationshipResponse(success=True, message="关系更新成功")
            except Exception as e:
                logger.error(f"更新用户关系失败: {e}")
                return UpdateRelationshipResponse(success=False, message=str(e))

        @self.router.put(
            "/person/{person_id}/impression",
            response_model=UpdateRelationshipResponse,
            summary="更新用户印象",
            description="更新指定用户的详细印象和简短印象",
        )
        async def update_person_impression(person_id: str, request: UpdateImpressionRequest, _=VerifiedDep):
            """更新用户印象"""
            try:
                from src.common.database.core.models import PersonInfo
                from src.common.database.core.session import get_db_session
                from sqlalchemy import select
                
                async with get_db_session() as session:
                    # 检查用户是否存在
                    stmt = select(PersonInfo).where(PersonInfo.person_id == person_id)
                    result = await session.execute(stmt)
                    person = result.scalar_one_or_none()
                    
                    if not person:
                        return UpdateRelationshipResponse(success=False, message="用户不存在")
                    
                    # 更新印象
                    if request.impression is not None:
                        person.impression = request.impression
                    if request.short_impression is not None:
                        person.short_impression = request.short_impression
                    
                    await session.commit()
                
                logger.info(f"用户 {person_id} 的印象更新成功")
                return UpdateRelationshipResponse(success=True, message="印象更新成功")
            except Exception as e:
                logger.error(f"更新用户印象失败: {e}")
                return UpdateRelationshipResponse(success=False, message=str(e))

        @self.router.put(
            "/person/{person_id}/points",
            response_model=UpdateRelationshipResponse,
            summary="更新用户记忆点",
            description="更新指定用户的记忆点列表",
        )
        async def update_person_points(person_id: str, points: list[dict[str, Any]], _=VerifiedDep):
            """更新用户记忆点"""
            try:
                from src.common.database.core.models import PersonInfo
                from src.common.database.core.session import get_db_session
                from sqlalchemy import select
                import orjson
                
                logger.info(f"开始更新用户 {person_id} 的记忆点，共 {len(points)} 个")
                
                async with get_db_session() as session:
                    # 检查用户是否存在
                    stmt = select(PersonInfo).where(PersonInfo.person_id == person_id)
                    result = await session.execute(stmt)
                    person = result.scalar_one_or_none()
                    
                    if not person:
                        logger.warning(f"用户 {person_id} 不存在")
                        return UpdateRelationshipResponse(success=False, message="用户不存在")
                    
                    # 转换为正确的格式 [(content, weight, timestamp), ...]
                    formatted_points = [
                        (point.get("content", ""), float(point.get("weight", 0)), point.get("timestamp", ""))
                        for point in points
                    ]
                    
                    # 序列化为JSON字符串存储
                    person.points = orjson.dumps(formatted_points).decode("utf-8")
                    
                    await session.commit()
                
                logger.info(f"用户 {person_id} 的记忆点更新成功")
                return UpdateRelationshipResponse(success=True, message="记忆点更新成功")
            except Exception as e:
                logger.error(f"更新用户记忆点失败: {e}", exc_info=True)
                return UpdateRelationshipResponse(success=False, message=str(e))

        @self.router.get(
            "/person/{person_id}/report",
            response_model=RelationshipReportResponse,
            summary="获取关系报告",
            description="生成指定用户的完整关系报告",
        )
        async def get_relationship_report(person_id: str, _=VerifiedDep):
            """获取关系报告"""
            try:
                report = await person_api.get_full_relationship_report(person_id)
                return RelationshipReportResponse(person_id=person_id, report=report)
            except Exception as e:
                logger.error(f"获取关系报告失败: {e}")
                return {"error": str(e)}

        @self.router.get(
            "/stats",
            summary="获取关系统计",
            description="获取系统关系统计信息",
        )
        async def get_relationship_stats(_=VerifiedDep):
            """获取关系统计"""
            try:
                stats = person_api.get_system_stats()
                return stats
            except Exception as e:
                logger.error(f"获取关系统计失败: {e}")
                return {"error": str(e)}

        @self.router.post(
            "/cache/clear",
            summary="清理关系缓存",
            description="清理指定用户或全部用户的关系缓存",
        )
        async def clear_relationship_cache(person_id: Optional[str] = None, _=VerifiedDep):
            """清理关系缓存"""
            try:
                person_api.clear_caches(person_id)
                return {"success": True, "message": "缓存清理成功"}
            except Exception as e:
                logger.error(f"清理关系缓存失败: {e}")
                return {"error": str(e)}

        @self.router.get(
            "/search",
            summary="搜索用户",
            description="根据用户名搜索用户",
        )
        async def search_person(query: str, _=VerifiedDep):
            """搜索用户"""
            try:
                person_id = await person_api.get_person_id_by_name(query)
                if not person_id:
                    return {"error": "未找到用户"}

                # 获取基础信息
                basic_info = await person_api.get_person_info(person_id)
                if not basic_info:
                    return {"error": "用户信息不存在"}

                return PersonBasicInfoResponse(person_id=person_id, person_name=basic_info.get("person_name", ""), nickname=basic_info.get("nickname"), know_times=basic_info.get("know_times", 0), know_since=basic_info.get("know_since"), last_know=basic_info.get("last_know"), attitude=basic_info.get("attitude"))
            except Exception as e:
                logger.error(f"搜索用户失败: {e}")
                return {"error": str(e)}
