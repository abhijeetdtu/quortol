const MARKDOWN_IMAGE_PATTERN = /!\[[^\]]*]\(([^)\s]+)(?:\s+"[^"]*")?\)/
const HTML_IMAGE_PATTERN = /<img[^>]+src=["']([^"']+)["']/i
const IMAGE_LINE_PATTERN = /^\s*!\[[^\]]*]\([^)]+\)\s*$/
const HTML_IMAGE_LINE_PATTERN = /^\s*<img[^>]+>\s*$/i
const HEADING_LINE_PATTERN = /^\s{0,3}#{1,6}\s+/
const HORIZONTAL_RULE_PATTERN = /^\s{0,3}(?:-{3,}|\*{3,}|_{3,})\s*$/
const VISUAL_HEADING_PATTERN = /^\s{0,3}#{2,6}\s+visual(?:\s*:?\s*.*)?$/i
const ITALIC_CAPTION_PATTERN = /^\s*(\*|_).+\1\s*$/
const LEAD_METADATA_LABELS = ['slug', 'author', 'date', 'published', 'updated', 'category', 'tags', 'series', 'status']

const findFirstNonEmptyLineIndex = (lines, start = 0) => {
  for (let index = start; index < lines.length; index += 1) {
    if (lines[index].trim()) {
      return index
    }
  }

  return -1
}

const removeLineAndFollowingBlanks = (lines, index) => {
  lines.splice(index, 1)
  while (index < lines.length && lines[index].trim() === '') {
    lines.splice(index, 1)
  }
}

const normalizeComparableText = (value = '') => {
  return value
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/['’"“”]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
}

const escapeForRegex = (value = '') => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const unwrapInlineEmphasis = (line = '') => {
  const trimmed = line.trim()
  const match = trimmed.match(/^(\*{1,3}|_{1,3})(.+)\1$/)
  if (!match) return trimmed
  return (match[2] || '').trim()
}

const isLeadMetadataLine = (line = '') => {
  const trimmed = line.trim()
  const match = trimmed.match(/^\*\*([^*]{1,40}):\*\*\s*.+$/)
  if (!match) return false

  const label = normalizeComparableText(match[1] || '')
  return LEAD_METADATA_LABELS.includes(label)
}

const isImageLine = (line = '') => IMAGE_LINE_PATTERN.test(line) || HTML_IMAGE_LINE_PATTERN.test(line)

const isHeadingLine = (line = '') => HEADING_LINE_PATTERN.test(line)

const isHorizontalRule = (line = '') => HORIZONTAL_RULE_PATTERN.test(line)

const stripDuplicateLeadHeading = (lines, title) => {
  const firstNonEmptyLineIndex = findFirstNonEmptyLineIndex(lines)
  if (firstNonEmptyLineIndex === -1) return

  const headingMatch = lines[firstNonEmptyLineIndex].match(/^#\s+(.+?)\s*$/)
  if (!headingMatch) return

  const headingText = normalizeComparableText(headingMatch[1] || '')
  const titleText = normalizeComparableText(title || '')
  if (!headingText || !titleText || headingText !== titleText) return

  removeLineAndFollowingBlanks(lines, firstNonEmptyLineIndex)
}

const stripLeadMetadataLines = (lines) => {
  let removedMetadata = false

  while (true) {
    const firstNonEmptyLineIndex = findFirstNonEmptyLineIndex(lines)
    if (firstNonEmptyLineIndex === -1) {
      return removedMetadata
    }

    if (!isLeadMetadataLine(lines[firstNonEmptyLineIndex])) {
      return removedMetadata
    }

    removedMetadata = true
    removeLineAndFollowingBlanks(lines, firstNonEmptyLineIndex)
  }
}

const stripLeadingRuleAfterMetadata = (lines, removedMetadata) => {
  if (!removedMetadata) return

  while (true) {
    const firstNonEmptyLineIndex = findFirstNonEmptyLineIndex(lines)
    if (firstNonEmptyLineIndex === -1) return
    if (!isHorizontalRule(lines[firstNonEmptyLineIndex])) return

    removeLineAndFollowingBlanks(lines, firstNonEmptyLineIndex)
  }
}

const stripDuplicateLeadByline = (lines) => {
  const firstNonEmptyLineIndex = findFirstNonEmptyLineIndex(lines)
  if (firstNonEmptyLineIndex === -1) return

  const candidate = unwrapInlineEmphasis(lines[firstNonEmptyLineIndex] || '')
  if (!/^(by|byline:)\b/i.test(candidate)) return

  removeLineAndFollowingBlanks(lines, firstNonEmptyLineIndex)
}

const isRedundantVisualHeadingBlock = (lines, headingIndex) => {
  let cursor = findFirstNonEmptyLineIndex(lines, headingIndex + 1)
  if (cursor === -1 || !isImageLine(lines[cursor])) {
    return false
  }

  cursor = findFirstNonEmptyLineIndex(lines, cursor + 1)
  while (cursor !== -1 && ITALIC_CAPTION_PATTERN.test(lines[cursor].trim())) {
    cursor = findFirstNonEmptyLineIndex(lines, cursor + 1)
  }

  if (cursor === -1) {
    return true
  }

  return isHorizontalRule(lines[cursor]) || isHeadingLine(lines[cursor])
}

const stripRedundantVisualHeadings = (lines) => {
  for (let index = 0; index < lines.length; index += 1) {
    if (!VISUAL_HEADING_PATTERN.test(lines[index])) continue
    if (!isRedundantVisualHeadingBlock(lines, index)) continue

    lines.splice(index, 1)
    if (index < lines.length && lines[index].trim() === '') {
      lines.splice(index, 1)
    }
    index -= 1
  }
}

const stripDuplicateHeroImage = (content, heroUrl) => {
  if (!heroUrl) return content

  const escapedUrl = escapeForRegex(heroUrl)
  const markdownPattern = new RegExp(
    `!\\[[^\\]]*\\]\\((?:\\s*<)?${escapedUrl}(?:>)?(?:\\s+["'][^"']*["'])?\\)`,
    'i'
  )
  if (markdownPattern.test(content)) {
    return content.replace(markdownPattern, '').replace(/\n{3,}/g, '\n\n')
  }

  const htmlPattern = new RegExp(`<img[^>]+src=["']${escapedUrl}["'][^>]*>`, 'i')
  if (htmlPattern.test(content)) {
    return content.replace(htmlPattern, '').replace(/\n{3,}/g, '\n\n')
  }

  return content
}

const normalizeMarkdownSpacing = (content = '') => {
  return content
    .replace(/\r\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

export const extractHeroImage = ({ content = '', featuredImage = '' } = {}) => {
  if (featuredImage) return featuredImage

  const markdownImageMatch = content.match(MARKDOWN_IMAGE_PATTERN)
  if (markdownImageMatch?.[1]) return markdownImageMatch[1]

  const htmlImageMatch = content.match(HTML_IMAGE_PATTERN)
  if (htmlImageMatch?.[1]) return htmlImageMatch[1]

  return ''
}

export const extractPlainTextFromMarkdown = (value = '') => {
  return value
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/`[^`]*`/g, ' ')
    .replace(/!\[[^\]]*]\([^)]+\)/g, ' ')
    .replace(/\[[^\]]*]\([^)]+\)/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[>*_~#-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

export const sanitizeBlogDisplayContent = ({ content = '', title = '', featuredImage = '' } = {}) => {
  if (!content) return ''

  const lines = content.replace(/\r\n/g, '\n').split('\n')
  stripDuplicateLeadHeading(lines, title)
  const removedMetadata = stripLeadMetadataLines(lines)
  stripLeadingRuleAfterMetadata(lines, removedMetadata)
  stripDuplicateLeadByline(lines)
  stripRedundantVisualHeadings(lines)

  const heroImage = extractHeroImage({ content, featuredImage })
  const cleanedContent = stripDuplicateHeroImage(lines.join('\n'), heroImage)

  return normalizeMarkdownSpacing(cleanedContent)
}
