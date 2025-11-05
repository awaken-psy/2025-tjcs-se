// .eslintrc.js
module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2021: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    parser: '@babel/eslint-parser',
    requireConfigFile: false
  },
  plugins: [
    'vue'
  ],
  rules: {
    // Vue 3 Composition API 全局宏
    'no-undef': 'off', // 关闭 no-undef，因为 Vue 宏是全局的

    // Vue 规则
    'vue/multi-word-component-names': 'off',
    'vue/html-self-closing': 'error',
    'vue/attribute-hyphenation': 'error',
    'vue/no-deprecated-slot-attribute': 'warn', // 将 slot 弃用警告改为警告而非错误

    // JavaScript 规则
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-unused-vars': 'warn', // 保持警告，但不禁用构建
    'no-case-declarations': 'off',

    // 代码风格规则
    'indent': ['error', 2],
    'quotes': ['error', 'single'],
    'semi': ['error', 'never'],
    'comma-dangle': ['error', 'only-multiline'],
    'space-before-function-paren': ['error', 'never']
  },
  // 定义 Vue 3 的全局宏
  globals: {
    defineProps: 'readonly',
    defineEmits: 'readonly',
    defineExpose: 'readonly',
    withDefaults: 'readonly'
  }
}