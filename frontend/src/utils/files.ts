export const MAX_FILE_BYTES = 1024 * 1024

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  return `${(bytes / 1024).toFixed(1)} KB`
}

export function isMarkdownFile(file: File): boolean {
  const name = file.name.toLocaleLowerCase()
  return name.endsWith('.md') || name.endsWith('.markdown')
}
