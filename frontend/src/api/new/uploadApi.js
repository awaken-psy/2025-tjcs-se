// src/api/uploadApi.js
// 上传相关API接口

import request from '@/utils/request'

/**
 * 上传文件
 * @param {File} file - 要上传的文件
 * @param {string} type - 文件类型 (image/video/other)
 * @returns {Promise}
 */
export const uploadFile = (file, type = '') => {
  const formData = new FormData()
  formData.append('file', file)
  if (type) {
    formData.append('type', type)
  }

  return request({
    url: '/upload',
    method: 'post',
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    data: formData
  })
}

