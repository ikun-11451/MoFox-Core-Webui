<template>
  <div class="relationship-view">
    <!-- 返回按钮 (详情页时) -->
    <div v-if="personDetail" class="top-bar">
      <button class="back-button" @click="backToList">
        <Icon icon="lucide:arrow-left" />
        <span>返回列表</span>
      </button>
    </div>

    <!-- 搜索栏 (列表页时) -->
    <div v-else class="search-bar">
      <div class="search-input-wrapper">
        <Icon icon="lucide:search" class="search-icon" />
        <input 
          v-model="searchQuery" 
          type="text" 
          class="search-input" 
          placeholder="搜索用户名..."
          @keyup.enter="handleSearch"
        />
        <button 
          v-if="searchQuery" 
          class="clear-button" 
          @click="clearSearch"
        >
          <Icon icon="lucide:x" />
        </button>
      </div>
      <button class="search-button" @click="handleSearch">
        <Icon icon="lucide:search" />
        <span>搜索</span>
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <Icon icon="lucide:alert-circle" class="error-icon" />
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button class="retry-button" @click="loadPersonDetail">
        <Icon icon="lucide:refresh-cw" />
        <span>重试</span>
      </button>
    </div>

    <!-- 用户详情 -->
    <div v-else-if="personDetail" class="person-detail">
      <!-- 基础信息卡片 -->
      <div class="info-card">
        <div class="card-header">
          <Icon icon="lucide:user" class="header-icon" />
          <h2>基础信息</h2>
        </div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <label>用户名</label>
              <span class="value">{{ personDetail.basic_info.person_name }}</span>
            </div>
            <div class="info-item">
              <label>昵称</label>
              <span class="value">{{ personDetail.basic_info.nickname || '未设置' }}</span>
            </div>
            <div class="info-item">
              <label>认识次数</label>
              <span class="value">{{ personDetail.basic_info.know_times }}</span>
            </div>
            <div class="info-item">
              <label>态度</label>
              <span class="value">{{ personDetail.basic_info.attitude || '未知' }}</span>
            </div>
            <div class="info-item full-width">
              <label>认识时间</label>
              <span class="value">{{ formatDate(personDetail.basic_info.know_since) }}</span>
            </div>
            <div class="info-item full-width">
              <label>最后见面</label>
              <span class="value">{{ formatDate(personDetail.basic_info.last_know) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 关系信息卡片 -->
      <div class="info-card">
        <div class="card-header">
          <Icon icon="lucide:heart" class="header-icon" />
          <h2>关系信息</h2>
          <button class="edit-button" @click="openEditRelationshipDialog">
            <Icon icon="lucide:edit-2" />
            <span>编辑</span>
          </button>
        </div>
        <div class="card-body">
          <div class="relationship-score">
            <label>关系分数</label>
            <div class="score-bar">
              <div 
                class="score-fill" 
                :style="{ width: `${personDetail.relationship.relationship_score * 100}%` }"
              ></div>
              <span class="score-text">{{ (personDetail.relationship.relationship_score * 100).toFixed(1) }}%</span>
            </div>
          </div>
          <div class="relationship-text">
            <label>关系描述</label>
            <p>{{ personDetail.relationship.relationship_text || '暂无描述' }}</p>
          </div>
        </div>
      </div>

      <!-- 印象卡片 -->
      <div class="info-card">
        <div class="card-header">
          <Icon icon="lucide:message-circle" class="header-icon" />
          <h2>我的印象</h2>
          <button class="edit-button" @click="openEditImpressionDialog">
            <Icon icon="lucide:edit-2" />
            <span>编辑</span>
          </button>
        </div>
        <div class="card-body">
          <div class="impression-section">
            <h3>详细印象</h3>
            <p class="impression-text">{{ personDetail.impression }}</p>
          </div>
          <div class="impression-section">
            <h3>简短印象</h3>
            <p class="impression-text short">{{ personDetail.short_impression }}</p>
          </div>
        </div>
      </div>

      <!-- 记忆点卡片 -->
      <div class="info-card">
        <div class="card-header">
          <Icon icon="lucide:bookmark" class="header-icon" />
          <h2>重要记忆点</h2>
          <button class="edit-button" @click="openEditMemoryPointsDialog">
            <Icon icon="lucide:edit-2" />
            <span>编辑</span>
          </button>
        </div>
        <div class="card-body">
          <div v-if="personDetail.memory_points.length === 0" class="empty-state">
            <p>暂无记忆点</p>
          </div>
          <div v-else class="memory-points-list">
            <div 
              v-for="(point, index) in personDetail.memory_points" 
              :key="index"
              class="memory-point"
            >
              <div class="point-header">
                <span class="point-weight">重要性: {{ point.weight.toFixed(2) }}</span>
                <span class="point-time">{{ formatDate(point.timestamp) }}</span>
              </div>
              <p class="point-content">{{ point.content }}</p>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- 用户列表 -->
    <div v-else class="person-list">
      <!-- 列表统计 -->
      <div class="list-header">
        <h2>用户列表</h2>
        <span class="count-badge">共 {{ totalCount }} 人</span>
      </div>

      <!-- 加载状态 -->
      <div v-if="listLoading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 用户卡片网格 -->
      <div v-else-if="personList.length > 0" class="person-grid">
        <div 
          v-for="person in personList" 
          :key="person.person_id"
          class="person-card"
          @click="viewPersonDetail(person.person_id)"
        >
          <div class="card-header">
            <div class="person-avatar">
              <Icon icon="lucide:user" />
            </div>
            <div class="person-info">
              <h3 class="person-name">{{ person.person_name }}</h3>
              <p v-if="person.nickname" class="person-nickname">{{ person.nickname }}</p>
            </div>
          </div>

          <div class="card-body">
            <div class="relation-score-mini">
              <label>关系分数</label>
              <div class="score-bar-mini">
                <div 
                  class="score-fill-mini" 
                  :style="{ width: `${person.relationship_score * 100}%` }"
                ></div>
                <span class="score-text-mini">{{ (person.relationship_score * 100).toFixed(0) }}%</span>
              </div>
            </div>

            <div v-if="person.relationship_text" class="relation-text-mini">
              <Icon icon="lucide:message-circle" class="mini-icon" />
              <span>{{ person.relationship_text }}</span>
            </div>

            <div v-if="person.short_impression" class="impression-mini">
              <Icon icon="lucide:sparkles" class="mini-icon" />
              <span>{{ person.short_impression }}</span>
            </div>

            <div class="card-footer">
              <div class="stat-item">
                <Icon icon="lucide:message-square" />
                <span>交互 {{ person.know_times }} 次</span>
              </div>
              <div v-if="person.last_know" class="stat-item">
                <Icon icon="lucide:clock" />
                <span>{{ formatDate(person.last_know) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <Icon icon="lucide:users" class="empty-icon" />
        <h3>暂无用户</h3>
        <p>还没有认识的用户</p>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          class="page-button" 
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          <Icon icon="lucide:chevron-left" />
          <span>上一页</span>
        </button>
        
        <div class="page-numbers">
          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-number"
            :class="{ active: page === currentPage }"
            @click="changePage(page)"
          >
            {{ page }}
          </button>
        </div>

        <button 
          class="page-button" 
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
        >
          <span>下一页</span>
          <Icon icon="lucide:chevron-right" />
        </button>
      </div>
    </div>

    <!-- 编辑关系信息对话框 -->
    <Teleport to="body">
      <Transition name="dialog-fade">
        <div v-if="showEditRelationshipDialog" class="dialog-overlay" @click="showEditRelationshipDialog = false">
          <div class="dialog edit-dialog" @click.stop>
            <div class="dialog-header">
              <h3>编辑关系信息</h3>
              <button class="close-button" @click="showEditRelationshipDialog = false">
                <Icon icon="lucide:x" />
              </button>
            </div>
            <div class="dialog-body">
              <div class="form-section">
                <div class="form-group">
                  <label>关系分数 (0-100)</label>
                  <input 
                    v-model.number="editForm.score" 
                    type="number" 
                    min="0" 
                    max="100" 
                    step="1"
                    class="form-input"
                  />
                  <div class="score-preview">
                    <div 
                      class="score-fill" 
                      :style="{ width: `${editForm.score}%` }"
                    ></div>
                  </div>
                </div>
                <div class="form-group">
                  <label>关系描述</label>
                  <textarea 
                    v-model="editForm.text" 
                    class="form-textarea"
                    rows="3"
                    placeholder="描述你与该用户的关系..."
                  ></textarea>
                </div>
              </div>
            </div>
            <div class="dialog-footer">
              <button class="cancel-button" @click="showEditRelationshipDialog = false">
                取消
              </button>
              <button class="confirm-button" @click="saveRelationship" :disabled="saving">
                {{ saving ? '保存中...' : '保存' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 编辑印象对话框 -->
    <Teleport to="body">
      <Transition name="dialog-fade">
        <div v-if="showEditImpressionDialog" class="dialog-overlay" @click="showEditImpressionDialog = false">
          <div class="dialog edit-dialog" @click.stop>
            <div class="dialog-header">
              <h3>编辑印象</h3>
              <button class="close-button" @click="showEditImpressionDialog = false">
                <Icon icon="lucide:x" />
              </button>
            </div>
            <div class="dialog-body">
              <div class="form-section">
                <div class="form-group">
                  <label>详细印象</label>
                  <textarea 
                    v-model="editForm.impression" 
                    class="form-textarea"
                    rows="4"
                    placeholder="详细描述你对该用户的印象..."
                  ></textarea>
                </div>
                <div class="form-group">
                  <label>简短印象</label>
                  <textarea 
                    v-model="editForm.shortImpression" 
                    class="form-textarea"
                    rows="2"
                    placeholder="一句话概括你的印象..."
                  ></textarea>
                </div>
              </div>
            </div>
            <div class="dialog-footer">
              <button class="cancel-button" @click="showEditImpressionDialog = false">
                取消
              </button>
              <button class="confirm-button" @click="saveImpression" :disabled="saving">
                {{ saving ? '保存中...' : '保存' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 编辑记忆点对话框 -->
    <Teleport to="body">
      <Transition name="dialog-fade">
        <div v-if="showEditMemoryPointsDialog" class="dialog-overlay" @click="showEditMemoryPointsDialog = false">
          <div class="dialog edit-dialog memory-dialog" @click.stop>
            <div class="dialog-header">
              <h3>编辑记忆点</h3>
              <button class="close-button" @click="showEditMemoryPointsDialog = false">
                <Icon icon="lucide:x" />
              </button>
            </div>
            <div class="dialog-body">
              <div class="form-section">
                <div class="section-header">
                  <h4><Icon icon="lucide:bookmark" /> 记忆点列表</h4>
                  <button class="add-point-btn" @click="addMemoryPoint" type="button">
                    <Icon icon="lucide:plus" />
                    添加
                  </button>
                </div>
                <div v-if="editForm.memoryPoints.length === 0" class="empty-hint">
                  暂无记忆点，点击"添加"按钮创建新记忆点
                </div>
                <div v-else class="memory-points-edit-list">
                  <div 
                    v-for="(point, index) in editForm.memoryPoints" 
                    :key="index"
                    class="memory-point-edit"
                  >
                    <div class="point-edit-header">
                      <label>重要性 (0-1)</label>
                      <input 
                        v-model.number="point.weight" 
                        type="number" 
                        min="0" 
                        max="1" 
                        step="0.01"
                        class="weight-input"
                      />
                      <button 
                        class="delete-point-btn" 
                        @click="deleteMemoryPoint(index)"
                        type="button"
                      >
                        <Icon icon="lucide:trash-2" />
                      </button>
                    </div>
                    <textarea 
                      v-model="point.content" 
                      class="form-textarea"
                      rows="2"
                      placeholder="描述这个记忆点..."
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>
            <div class="dialog-footer">
              <button class="cancel-button" @click="showEditMemoryPointsDialog = false">
                取消
              </button>
              <button class="confirm-button" @click="saveMemoryPoints" :disabled="saving">
                {{ saving ? '保存中...' : '保存' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { 
  getPersonList,
  getPersonDetail, 
  updatePersonRelationship, 
  searchPerson,
  type PersonDetail,
  type PersonCard 
} from '@/api/relationship'
import { showSuccess, showError } from '@/utils/dialog'

const searchQuery = ref('')
const loading = ref(false)
const error = ref('')
const personDetail = ref<PersonDetail | null>(null)
const currentPersonId = ref('')

// 列表相关状态
const personList = ref<PersonCard[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const totalPages = ref(0)
const totalCount = ref(0)
const listLoading = ref(false)

const showEditRelationshipDialog = ref(false)
const showEditImpressionDialog = ref(false)
const showEditMemoryPointsDialog = ref(false)
const saving = ref(false)

const editForm = reactive({
  score: 0,
  text: '',
  impression: '',
  shortImpression: '',
  memoryPoints: [] as Array<{ content: string; weight: number; timestamp: string }>
})

// 加载用户列表
const loadPersonList = async () => {
  listLoading.value = true
  error.value = ''
  
  try {
    const result = await getPersonList(currentPage.value, pageSize.value)
    if (result.success && result.data) {
      personList.value = result.data.persons
      totalPages.value = result.data.total_pages
      totalCount.value = result.data.total
    } else {
      error.value = result.error || '加载用户列表失败'
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
  } finally {
    listLoading.value = false
  }
}

// 页面加载时获取用户列表
onMounted(() => {
  loadPersonList()
})

// 计算可见的页码
const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  
  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const clearSearch = () => {
  searchQuery.value = ''
}

const changePage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  await loadPersonList()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const viewPersonDetail = async (personId: string) => {
  currentPersonId.value = personId
  await loadPersonDetail()
}

const backToList = () => {
  personDetail.value = null
  currentPersonId.value = ''
  searchQuery.value = ''
  loadPersonList()
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    await showError('请输入用户名')
    return
  }

  loading.value = true
  error.value = ''
  personDetail.value = null

  try {
    const result = await searchPerson(searchQuery.value.trim())
    if (result.success && result.data) {
      currentPersonId.value = result.data.person_id
      await loadPersonDetail()
    } else {
      error.value = result.error || '未找到用户'
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '搜索失败'
  } finally {
    loading.value = false
  }
}

const loadPersonDetail = async () => {
  if (!currentPersonId.value) return

  loading.value = true
  error.value = ''

  try {
    const result = await getPersonDetail(currentPersonId.value)
    if (result.success && result.data) {
      personDetail.value = result.data
      // 初始化编辑表单
      editForm.score = result.data.relationship.relationship_score * 100
      editForm.text = result.data.relationship.relationship_text || ''
    } else {
      error.value = result.error || '加载用户详情失败'
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
  } finally {
    loading.value = false
  }
}

// 打开编辑关系信息对话框
const openEditRelationshipDialog = () => {
  if (!personDetail.value) return
  
  // 初始化表单数据
  editForm.score = personDetail.value.relationship.relationship_score * 100
  editForm.text = personDetail.value.relationship.relationship_text || ''
  
  showEditRelationshipDialog.value = true
}

// 打开编辑印象对话框
const openEditImpressionDialog = () => {
  if (!personDetail.value) return
  
  // 初始化表单数据
  editForm.impression = personDetail.value.impression || ''
  editForm.shortImpression = personDetail.value.short_impression || ''
  
  showEditImpressionDialog.value = true
}

// 打开编辑记忆点对话框
const openEditMemoryPointsDialog = () => {
  if (!personDetail.value) return
  
  // 初始化表单数据
  editForm.memoryPoints = personDetail.value.memory_points.map(p => ({
    content: p.content,
    weight: p.weight,
    timestamp: p.timestamp
  }))
  
  showEditMemoryPointsDialog.value = true
}

// 添加记忆点
const addMemoryPoint = () => {
  editForm.memoryPoints.push({
    content: '',
    weight: 0.5,
    timestamp: new Date().toISOString()
  })
}

// 删除记忆点
const deleteMemoryPoint = (index: number) => {
  editForm.memoryPoints.splice(index, 1)
}

// 保存关系信息
const saveRelationship = async () => {
  if (!currentPersonId.value) return

  saving.value = true

  try {
    // 更新关系信息
    const result = await updatePersonRelationship(currentPersonId.value, {
      relationship_score: editForm.score / 100,
      relationship_text: editForm.text
    })

    if (!result.success) {
      throw new Error(result.error || '更新关系信息失败')
    }

    // 检查返回的数据中的 success 字段
    if (result.data && !result.data.success) {
      throw new Error(result.data.message || '更新关系信息失败')
    }

    await showSuccess('关系信息已更新')
    showEditRelationshipDialog.value = false
    await loadPersonDetail()
  } catch (err) {
    await showError(err instanceof Error ? err.message : '更新失败')
  } finally {
    saving.value = false
  }
}

// 保存印象
const saveImpression = async () => {
  if (!currentPersonId.value) return

  saving.value = true

  try {
    // 更新印象信息
    const { updatePersonImpression } = await import('@/api/relationship')
    
    const result = await updatePersonImpression(
      currentPersonId.value,
      editForm.impression,
      editForm.shortImpression
    )

    if (!result.success) {
      throw new Error(result.error || '更新印象失败')
    }

    // 检查返回的数据中的 success 字段
    if (result.data && !result.data.success) {
      throw new Error(result.data.message || '更新印象失败')
    }

    await showSuccess('印象已更新')
    showEditImpressionDialog.value = false
    await loadPersonDetail()
  } catch (err) {
    await showError(err instanceof Error ? err.message : '更新失败')
  } finally {
    saving.value = false
  }
}

// 保存记忆点
const saveMemoryPoints = async () => {
  if (!currentPersonId.value) return

  saving.value = true

  try {
    // 更新记忆点
    const { updatePersonPoints } = await import('@/api/relationship')
    
    const result = await updatePersonPoints(
      currentPersonId.value,
      editForm.memoryPoints
    )

    if (!result.success) {
      throw new Error(result.error || '更新记忆点失败')
    }

    // 检查返回的数据中的 success 字段
    if (result.data && !result.data.success) {
      throw new Error(result.data.message || '更新记忆点失败')
    }

    await showSuccess('记忆点已更新')
    showEditMemoryPointsDialog.value = false
    await loadPersonDetail()
  } catch (err) {
    await showError(err instanceof Error ? err.message : '更新失败')
  } finally {
    saving.value = false
  }
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '未知'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN')
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
.relationship-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* 顶部栏 */
.top-bar {
  margin-bottom: 24px;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.search-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 14px;
  font-size: 20px;
  color: var(--text-tertiary);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 44px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 15px;
  transition: all var(--transition);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.clear-button {
  position: absolute;
  right: 8px;
  padding: 6px;
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition);
}

.clear-button:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.search-button,
.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary);
  border: none;
  border-radius: var(--radius);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
}

.back-button {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.search-button:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.back-button:hover {
  background: var(--bg-quaternary);
  border-color: var(--primary);
}

/* 用户列表 */
.person-list {
  width: 100%;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.list-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.count-badge {
  padding: 6px 14px;
  background: var(--primary-bg);
  color: var(--primary);
  border-radius: var(--radius-full);
  font-size: 14px;
  font-weight: 600;
}

/* 用户卡片网格 */
.person-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.person-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 20px;
  cursor: pointer;
  transition: all var(--transition);
}

.person-card:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.person-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  flex-shrink: 0;
}

.person-info {
  flex: 1;
  min-width: 0;
}

.person-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.person-nickname {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: var(--text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.relation-score-mini label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.score-bar-mini {
  position: relative;
  height: 24px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.score-fill-mini {
  height: 100%;
  background: linear-gradient(90deg, var(--primary) 0%, var(--success) 100%);
  transition: width 0.3s ease;
}

.score-text-mini {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: 700;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.relation-text-mini,
.impression-mini {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.mini-icon {
  font-size: 16px;
  color: var(--text-tertiary);
  flex-shrink: 0;
  margin-top: 2px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.stat-item svg {
  font-size: 14px;
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 32px;
}

.page-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}

.page-button:hover:not(:disabled) {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(59, 130, 246, 0.05);
}

.page-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 8px;
}

.page-number {
  min-width: 40px;
  height: 40px;
  padding: 0 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}

.page-number:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(59, 130, 246, 0.05);
}

.page-number.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

/* 加载和错误状态 */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 48px;
  color: var(--danger);
  margin-bottom: 16px;
}

.retry-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  margin-top: 16px;
  background: var(--primary);
  border: none;
  border-radius: var(--radius);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
}

.retry-button:hover {
  background: var(--primary-dark);
}

/* 空状态 */
.empty-state-main {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  color: var(--text-tertiary);
  margin-bottom: 16px;
  opacity: 0.5;
}

/* 信息卡片 */
.info-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  margin-bottom: 20px;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.header-icon {
  font-size: 24px;
  color: var(--primary);
}

.card-header h2 {
  flex: 1;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.edit-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--primary);
  border: none;
  border-radius: var(--radius);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}

.edit-button:hover {
  background: var(--primary-dark);
}

.card-body {
  padding: 24px;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item .value {
  font-size: 16px;
  color: var(--text-primary);
  font-weight: 500;
}

/* 关系分数 */
.relationship-score {
  margin-bottom: 24px;
}

.relationship-score label {
  display: block;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.score-bar {
  position: relative;
  height: 32px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary) 0%, var(--success) 100%);
  transition: width 0.3s ease;
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 14px;
  font-weight: 700;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.relationship-text label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.relationship-text p {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-primary);
}

/* 印象 */
.impression-section {
  margin-bottom: 20px;
}

.impression-section:last-child {
  margin-bottom: 0;
}

.impression-section h3 {
  margin: 0 0 10px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
}

.impression-text {
  margin: 0;
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-wrap;
}

.impression-text.short {
  font-style: italic;
  color: var(--text-secondary);
}

/* 记忆点 */
.memory-points-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.memory-point {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius);
  border-left: 3px solid var(--primary);
}

.point-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--text-tertiary);
}

.point-weight {
  font-weight: 600;
  color: var(--primary);
}

.point-content {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-primary);
}

.empty-state {
  padding: 40px;
  text-align: center;
  color: var(--text-tertiary);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.action-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 20px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
}

.action-button:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(59, 130, 246, 0.05);
}

.report-button:hover {
  border-color: var(--success);
  color: var(--success);
  background: rgba(34, 197, 94, 0.05);
}

.cache-button:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: rgba(239, 68, 68, 0.05);
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.dialog {
  width: 100%;
  max-width: 500px;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.edit-dialog {
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.edit-dialog .dialog-body {
  overflow-y: auto;
  max-height: calc(90vh - 140px);
}

.memory-dialog {
  max-width: 700px;
}

.memory-dialog .dialog-body {
  max-height: calc(90vh - 140px);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-button {
  padding: 6px;
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition);
}

.close-button:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.dialog-body {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 15px;
  transition: all var(--transition);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 15px;
  font-family: inherit;
  resize: vertical;
  transition: all var(--transition);
}

.form-textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.score-preview {
  margin-top: 12px;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

/* 表单分区 */
.form-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.form-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.add-point-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: var(--primary);
  border: none;
  border-radius: var(--radius);
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}

.add-point-btn:hover {
  background: var(--primary-dark);
}

.empty-hint {
  padding: 20px;
  text-align: center;
  color: var(--text-tertiary);
  font-size: 14px;
  background: var(--bg-tertiary);
  border-radius: var(--radius);
}

/* 记忆点编辑列表 */
.memory-points-edit-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.memory-point-edit {
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
}

.point-edit-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.point-edit-header label {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-tertiary);
}

.weight-input {
  width: 100px;
  padding: 6px 10px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 14px;
  transition: all var(--transition);
}

.weight-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.delete-point-btn {
  margin-left: auto;
  display: flex;
  align-items: center;
  padding: 6px;
  background: transparent;
  border: 1px solid var(--danger);
  border-radius: var(--radius);
  color: var(--danger);
  cursor: pointer;
  transition: all var(--transition);
}

.delete-point-btn:hover {
  background: var(--danger);
  color: white;
}

.score-preview .score-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary) 0%, var(--success) 100%);
  transition: width 0.3s ease;
}

.report-content {
  margin: 0;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius);
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.cancel-button,
.confirm-button {
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
}

.cancel-button {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.cancel-button:hover {
  background: var(--bg-quaternary);
}

.confirm-button {
  background: var(--primary);
  color: white;
}

.confirm-button:hover:not(:disabled) {
  background: var(--primary-dark);
}

.confirm-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 对话框过渡动画 */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-fade-enter-active .dialog,
.dialog-fade-leave-active .dialog {
  transition: transform 0.3s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-fade-enter-from .dialog,
.dialog-fade-leave-to .dialog {
  transform: scale(0.9) translateY(-20px);
}

/* 响应式 */
@media (max-width: 768px) {
  .relationship-view {
    padding: 16px;
  }

  .search-bar {
    flex-direction: column;
    gap: 8px;
  }

  .back-button span,
  .search-button span {
    display: none;
  }

  .person-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .pagination {
    flex-wrap: wrap;
  }

  .page-numbers {
    order: 3;
    width: 100%;
    justify-content: center;
    margin-top: 8px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .dialog {
    max-width: 100%;
  }
}
</style>
