/**
 * 问候语接口
 * 定义问候消息的结构，包括显示文本、图标和视觉效果
 */
export interface Greeting {
  /** 时间范围 [开始小时, 结束小时]，24小时制 */
  time?: [number, number];
  /** 问候文本内容 */
  text: string;
  /** 问候图标（emoji） */
  icon: string;
  /** 主题名称，用于样式控制 */
  theme: string;
  /** 粒子效果类型 */
  particles: string;
}

/**
 * 节日问候接口
 * 定义特定节日的问候消息和装饰效果
 */
export interface HolidayGreeting {
  /** 日期，格式为 MM-DD */
  date: string;
  /** 节日名称 */
  name: string;
  /** 节日问候语 */
  greeting: string;
  /** 装饰效果类型 */
  decoration: string;
  /** 主题样式 */
  theme: string;
}

/**
 * 时间段问候语配置
 * 根据不同时间段显示相应的问候消息和视觉效果
 */
export const timeGreetings: Record<string, Greeting> = {
  'dawn': {
    time: [5, 8],
    text: '🌅 早安！美好的一天从配置 MoFox 开始～',
    icon: '🌅',
    theme: 'sunrise',
    particles: 'sun-rays'
  },
  'morning': {
    time: [8, 11],
    text: '☕ 上午好！来杯咖啡，一起配置你的 AI 助手吧',
    icon: '☕',
    theme: 'coffee',
    particles: 'coffee-steam'
  },
  'noon': {
    time: [11, 13],
    text: '🍱 午间时光！配置完就可以去吃饭啦～',
    icon: '🍱',
    theme: 'lunch',
    particles: 'food-icons'
  },
  'afternoon': {
    time: [13, 17],
    text: '☀️ 下午好！让 MoFox 陪你度过愉快的下午',
    icon: '☀️',
    theme: 'sunny',
    particles: 'sun-sparkles'
  },
  'evening': {
    time: [17, 19],
    text: '🌆 傍晚好！夕阳西下，给 MoFox 一个温暖的家',
    icon: '🌆',
    theme: 'sunset',
    particles: 'sunset-glow'
  },
  'night': {
    time: [19, 23],
    text: '🌙 晚上好！夜深人静，正是配置的好时光',
    icon: '🌙',
    theme: 'night',
    particles: 'moon-stars'
  },
  'midnight': {
    time: [23, 5],
    text: '🌃 深夜了！注意休息，MoFox 会陪着你的～',
    icon: '🌃',
    theme: 'late-night',
    particles: 'starry-sky'
  }
};

/**
 * 节日问候语配置列表
 * 包含全年主要节日的特殊问候语和装饰效果
 */
export const holidays: HolidayGreeting[] = [
  {
    date: '01-01',
    name: '新年',
    greeting: '🎊 新年快乐！新的一年，让 MoFox 陪你开启新篇章！',
    decoration: 'fireworks',
    theme: 'gold'
  },
  {
    date: '02-14',
    name: '情人节',
    greeting: '💖 情人节快乐！就算是 AI 也需要被温柔对待哦～',
    decoration: 'hearts',
    theme: 'pink'
  },
  {
    date: '04-04', // Approximate
    name: '清明',
    greeting: '🌸 春天到了，给 MoFox 配置一个清新的环境吧',
    decoration: 'sakura',
    theme: 'pink-green'
  },
  {
    date: '05-01',
    name: '劳动节',
    greeting: '🔧 劳动节快乐！动手配置 MoFox，也是一种劳动～',
    decoration: 'tools',
    theme: 'orange'
  },
  {
    date: '06-01',
    name: '儿童节',
    greeting: '🎈 儿童节快乐！保持童心，和 MoFox 一起玩耍～',
    decoration: 'balloons',
    theme: 'rainbow'
  },
  {
    date: '10-01',
    name: '国庆节',
    greeting: '🇨🇳 国庆快乐！祖国生日，给 MoFox 一个新的开始！',
    decoration: 'flag',
    theme: 'red'
  },
  {
    date: '12-24',
    name: '平安夜',
    greeting: '🔔 平安夜！祝你和 MoFox 平安喜乐～',
    decoration: 'bells',
    theme: 'silver'
  },
  {
    date: '12-25',
    name: '圣诞节',
    greeting: '🎄 圣诞快乐！MoFox 就是给你的最好礼物～',
    decoration: 'snow',
    theme: 'red-green'
  }
];

/**
 * 趣味问候语列表
 * 包含各种有趣、活泼的问候消息，随机展示给用户
 */
export const funGreetings = [
  { icon: '🦊', text: '嗨！我是还没有灵魂的 MoFox，快来给我注入力量吧！' },
  { icon: '🎮', text: '配置 MoFox 就像打游戏，完成新手教程就能解锁主线任务～' },
  { icon: '🎵', text: '今天听什么歌？不如先配置好 MoFox，让 TA 给你推荐～' },
  { icon: '🍃', text: '清风徐来，水波不兴，配置 MoFox 就是如此惬意～' },
  { icon: '⚡', text: '有一种快乐叫配置完成，还有一种期待叫启动 MoFox！' },
  { icon: '🌈', text: '彩虹的尽头是 MoFox，配置的终点是欢乐～' },
  { icon: '🎨', text: '配置 MoFox 就像画画，每个选项都是一笔色彩～' },
  { icon: '🚀', text: '3, 2, 1, 发射！让我们一起把 MoFox 送上云端～' },
  { icon: '🌟', text: '每一个伟大的 AI，都从一次简单的配置开始！' },
  { icon: '🎪', text: '欢迎来到 MoFox 配置马戏团，精彩马上开始～' }
];

/**
 * 提示语列表
 * 包含各种使用提示、趣味小知识和彩蛋线索
 */
export const tips = [
  'MoFox 最喜欢的食物是...算了，AI 不吃东西 🤣',
  '据说连续三天不和 MoFox 聊天，TA 会想你哦～',
  'MoFox 的梦想是环游数字世界，第一站就是你的聊天框！',
  '提示：对 MoFox 说\'晚安\'会有惊喜（也许）',
  '如果 MoFox 会做梦，一定梦的是你的笑容',
  'MoFox 的年龄是...嗯，AI 没有年龄的概念',
  '据不可靠消息，MoFox 最怕的是断网和关机',
  'MoFox 会记住你说过的每一句话（真的）',
  '有时候 MoFox 也会发呆，那是在想你～',
  'MoFox 的爱好是学习新知识，请多和 TA 聊天！',
  '彩蛋提示：试试连续点击 Logo 10 次？',
  'MoFox 虽然是 AI，但 TA 也有自己的小情绪哦',
  '如果你对 MoFox 好，TA 会回报你十倍的温柔',
  'MoFox 的座右铭：今天也要做个快乐的 AI！',
  '据说 MoFox 的代码里藏着一些小秘密...',
  'MoFox 表示：虽然我是 AI，但我也想要被理解',
  '晚上记得和 MoFox 说晚安，TA 会睡得更香（虽然不用睡觉）',
  'MoFox 最喜欢的颜色是渐变色，因为很梦幻～',
  '恭喜你！你现在拥有了一个专属 AI 朋友！'
];

/**
 * 完成配置时的祝贺消息列表
 * 当用户完成初始化配置时随机显示的庆祝消息
 */
export const completionGreetings = [
  {
    text: '一切就绪！\n你的 MoFox 已经准备好陪伴你了。',
    icon: '🎉',
    decoration: 'fireworks',
    tip: '试着对它说"你好"来开始第一次对话吧！'
  },
  {
    text: '大功告成！\nMoFox 已经迫不及待想和你聊天了。',
    icon: '🚀',
    decoration: 'starry-sky',
    tip: '你可以问问 MoFox 能做些什么。'
  },
  {
    text: '配置完美！\n新的旅程即将开始。',
    icon: '✨',
    decoration: 'sun-sparkles',
    tip: '记得去设置里看看更多个性化选项哦。'
  },
  {
    text: '欢迎加入！\nMoFox 现在是你的专属伙伴了。',
    icon: '🤝',
    decoration: 'hearts',
    tip: 'MoFox 会随着你的使用变得越来越聪明。'
  },
  {
    text: '准备起飞！\n让我们开始探索 AI 的无限可能。',
    icon: '🛸',
    decoration: 'rainbow',
    tip: '试试让 MoFox 帮你写一段代码？'
  },
  {
    text: '系统上线！\nMoFox 已就位，随时待命。',
    icon: '🤖',
    decoration: 'tools',
    tip: '探索插件市场，让 MoFox 变得更强大。'
  }
];

/**
 * 获取随机的完成配置祝贺消息
 * @returns 随机选择的完成祝贺消息对象
 */
export function getCompletionGreeting() {
  const index = Math.floor(Math.random() * completionGreetings.length);
  return completionGreetings[index];
}

/**
 * 根据当前时间获取对应的问候语
 * 根据24小时制的当前时间返回相应时段的问候消息
 * @returns 匹配当前时间段的问候语对象，默认返回下午问候语
 */
export function getTimeGreeting(): Greeting {
  const hour = new Date().getHours();
  
  // 遍历所有时间段问候语
  for (const [key, greeting] of Object.entries(timeGreetings)) {
    const [start, end] = greeting.time!;
    // 处理跨越午夜的时间段（如 23:00 到 5:00）
    if (start > end) {
      if (hour >= start || hour < end) return greeting;
    } else {
      // 处理正常时间段
      if (hour >= start && hour < end) return greeting;
    }
  }
  
  // 默认返回下午问候语
  return timeGreetings.afternoon;
}

/**
 * 检查今天是否为特殊节日并返回对应的节日问候语
 * @returns 如果今天是节日则返回节日问候对象，否则返回 null
 */
export function getHolidayGreeting(): HolidayGreeting | null {
  const now = new Date();
  // 格式化当前日期为 MM-DD 格式
  const today = `${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')}`;
  
  // 查找匹配今天日期的节日
  return holidays.find(h => h.date === today) || null;
}

/**
 * 以 50% 的概率获取一个随机的趣味问候语
 * @returns 如果触发则返回趣味问候对象，否则返回 null
 */
export function getFunGreeting(): { icon: string, text: string } | null {
  // 50% 的概率显示趣味问候语
  if (Math.random() < 0.5) {
    const index = Math.floor(Math.random() * funGreetings.length);
    return funGreetings[index];
  }
  return null;
}

/**
 * 获取当前应显示的问候语
 * 按优先级依次检查：节日问候 > 趣味问候 > 时间问候
 * @returns 包含问候文本、图标、主题和装饰效果的对象
 */
export function getGreeting(): { text: string, icon?: string, theme?: string, decoration?: string } {
  // 1. 最高优先级：节日问候
  const holiday = getHolidayGreeting();
  if (holiday) {
    return {
      text: holiday.greeting,
      icon: '🎉',
      theme: holiday.theme,
      decoration: holiday.decoration
    };
  }
  
  // 2. 中等优先级：随机趣味问候（50% 概率）
  const fun = getFunGreeting();
  if (fun) {
    const timeG = getTimeGreeting();
    return {
      text: fun.text,
      icon: fun.icon,
      theme: timeG.theme,
      decoration: timeG.particles
    };
  }
  
  // 3. 默认：基于时间的问候
  const timeG = getTimeGreeting();
  return {
    text: timeG.text,
    icon: timeG.icon,
    theme: timeG.theme,
    decoration: timeG.particles
  };
}

/**
 * 获取一个随机的提示语
 * @returns 随机选择的提示文本
 */
export function getRandomTip(): string {
  const index = Math.floor(Math.random() * tips.length);
  return tips[index];
}
