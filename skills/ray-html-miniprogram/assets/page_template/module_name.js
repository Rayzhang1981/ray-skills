// 小程序页面逻辑模板 - 根据HTML的JavaScript转换
const { function1, function2 } = require('../../utils/calc_module.js');  // 导入计算逻辑

Page({
  data: {
    title: '模块标题',
    subtitle: 'Module Subtitle',
    
    // 输入字段定义（从HTML的input value提取）
    inputs: [
      { id: 'field1', label: '字段1 Label', value: '2.0', placeholder: '输入值' },
      { id: 'field2', label: '字段2 Label', value: '5.0', placeholder: '输入值' }
    ],
    
    // 选择字段定义（如封头类型，从HTML的select options提取）
    selects: [
      {
        id: 'selectField',
        label: '选择项 Label',
        options: [
          { value: 'option1', label: '选项1 Option1' },
          { value: 'option2', label: '选项2 Option2' }
        ],
        selectedIndex: 0
      }
    ],
    
    // 计算结果
    result: null,
    resultItems: [],
    tableData: []
  },

  onLoad() {
    // 页面加载时的初始化
  },

  // 输入框变化处理
  onInputChange(e) {
    const field = e.currentTarget.dataset.field;
    const value = e.detail.value;
    
    const inputs = this.data.inputs.map(item => {
      if (item.id === field) {
        return { ...item, value };
      }
      return item;
    });
    
    this.setData({ inputs });
  },

  // 选择器变化处理
  onSelectChange(e) {
    const field = e.currentTarget.dataset.field;
    const index = e.detail.value;
    
    const selects = this.data.selects.map(item => {
      if (item.id === field) {
        return { ...item, selectedIndex: index };
      }
      return item;
    });
    
    this.setData({ selects });
  },

  // 计算按钮点击
  calculate() {
    // 收集输入数据
    const inputData = {};
    this.data.inputs.forEach(item => {
      inputData[item.id] = parseFloat(item.value) || 0;
    });
    
    this.data.selects.forEach(item => {
      inputData[item.id] = item.options[item.selectedIndex].value;
    });

    // 调用计算函数（从HTML提取的）
    try {
      const result = function1(inputData);
      
      // 格式化结果用于显示
      const resultItems = [
        { label: '结果1', value: result.value1.toFixed(2), unit: 'm³', highlight: true },
        { label: '结果2', value: result.value2.toFixed(2), unit: 'L', highlight: false }
      ];
      
      this.setData({
        result: true,
        resultItems
      });
      
      // 如果需要生成表格（如容积表）
      if (result.table) {
        this.generateTable(result.table);
      }
      
    } catch (error) {
      wx.showToast({
        title: '计算错误：' + error.message,
        icon: 'none',
        duration: 2000
      });
    }
  },

  // 生成表格数据（如容积表）
  generateTable(tableData) {
    const table = tableData.map(item => ({
      height: item.height.toFixed(2),
      volume: item.volume.toFixed(2)
    }));
    
    this.setData({ tableData: table });
  }
});
