import { describe, it, expect } from 'vitest'

// 简单的数学测试
describe('Basic Math Tests', () => {
  it('should add numbers correctly', () => {
    expect(1 + 1).toBe(2)
    expect(2 + 3).toBe(5)
  })

  it('should multiply numbers correctly', () => {
    expect(2 * 3).toBe(6)
    expect(5 * 5).toBe(25)
  })
})

// 字符串操作测试
describe('String Operations', () => {
  it('should convert to uppercase', () => {
    expect('hello'.toUpperCase()).toBe('HELLO')
  })

  it('should check string length', () => {
    expect('test').toHaveLength(4)
    expect('').toHaveLength(0)
  })
})