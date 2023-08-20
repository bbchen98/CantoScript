## 粤语注音排版脚本

### 1 功能简介
本脚本解决粤语注音和文字的排版问题。

脚本可将音标与汉字一一对应，并输出为pdf文件。整齐美观。

### 2 使用方法
#### 2.1 依赖库
依赖库只有一个：`reportlab`，版本为4.0.4

#### 2.1 输入说明
将输入的txt文件放在当前目录下的`txt`目录中。

txt中，音标在上，文字在下。示例如下：
```
ne`i5ho4yi5ci2zung1bedd1xudd3wa6
你何以始终不说话
ze^n6gun2gang2ce^dd1bedd1fai3ba6
尽管讲出不快吧
```

空格和空行都会被忽略。

为方便输入，这里使用一些符号组合来代替键盘打不出来的音标：
- e` 会被替换为 é
- e^ 会被替换为 ê
- u: 会被替换为 ü

为了方便表示粤语中的闭口音，这里用重复的字符来表示。例如`dd`会被转化为加粗的`d`。

输出的pdf文件会生成在`lyrics`目录下。  

这两个目录下都有两个实例，可以看下。

