"""
粤语词音排版
功能：读取.txt文本，将文字和音标对齐，输出为pdf
作者：cbb
日期：2023/07/30
"""
from enum import Enum
import os
import re

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.lib.pagesizes import A4
from reportlab.platypus.tables import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class RTFlag(Enum):
    FAIL = 0
    SUCCESS = 1


class CantoScript(object):
    def __init__(self, regeneration=False):
        self.title = None
        self.output_lst = list()
        self.max_cols = 0
        self.input_file_path = './txt'
        self.output_file_path = './lyrics'
        self.regeneration = regeneration
        self.replace_dict = {
            'e`': 'é',
            'e^': 'ê',
            'u:': 'ü',
            'dd': '<u><b>d</b></u>',
            'gg': '<u><b>g</b></u>',
            'mm': '<u><b>m</b></u>',
            'bb': '<u><b>b</b></u>',
        }

    def start(self):
        """
        功能：处理文本，生成pdf
        :return:
        """
        # 检查输入输出目录是否存在
        if self._check_filepath() != RTFlag.SUCCESS:
            self._log("PROCESS_ERROR", "The file directory does not exist.")

        # 逐个处理输入目录中的文件
        file_lst = os.listdir(self.input_file_path)
        for fl in file_lst:
            output_file = fl[:fl.find(".")] + ".pdf"
            if not self.regeneration and os.path.exists(os.path.join(self.output_file_path, output_file)):
                self._log("PROCESS_SKIP", "[" + output_file + "] already exists, skipping it.")
                continue

            if self._process_text(fl) != RTFlag.SUCCESS:
                self._log("PROCESS_ERROR", "Error processing to [" + fl + "].")
                return RTFlag.FAIL

            # Output as a PDF file
            if self._output_to_pdf() != RTFlag.SUCCESS:
                self._log("PROCESS_ERROR", "Failed to generate PDF.")

            # Reinit the global value
            self.max_cols = 0
            self.title = None
            self.output_lst.clear()

            # Log
            self._log("PROCESS_SUCCESS", "[" + output_file + "] has been successfully generated.")

        # Completed
        self._log("SUCCESS", "All files processed.")

    def _check_filepath(self):
        """
        检验当前输入和输出目录是否存在
        输入目录不存在就抛异常
        输出目录不在就创建一个
        :return:
        """
        # 输入目录不存在就报错
        if not os.path.exists(self.input_file_path):
            self._log('FILE_FAIL', 'The lyrics source file directory does not exist.')
            return RTFlag.SUCCESS
        # 输出目录不存在就创建
        if not os.path.exists(self.output_file_path):
            os.makedirs(self.output_file_path)

        return RTFlag.SUCCESS

    def _log(self, logType, message):
        print(logType + ": " + message)

    def _process_text(self, filename):
        """
        处理文本，按行处理
        :return:
        """
        # load file
        file_path = os.path.join(self.input_file_path, filename)
        if not os.path.exists(file_path):
            self._log('FILE_ERROR', 'The' + file_path + 'file does not exist.')
            return RTFlag.FAIL

        # get the lyrics title
        self.title = filename[: filename.find('.')]

        # load the lyrics
        lyrs_lst = list()
        with open(file_path, "r", encoding='utf-8') as text_file:
            for line in text_file:
                lyrs_lst.append(line.strip().replace(" ", ""))

        # Handle the symbols and lyrics
        if self._format_symbols_and_lyrics(lyrs_lst) != RTFlag.SUCCESS:
            self._log("PROCESS_ERROR", "Error processing to [" + filename + "].")
            return RTFlag.FAIL

        return RTFlag.SUCCESS

    def _format_symbols_and_lyrics(self, lyrics_lst):
        """
        将音标和歌词一一匹配，将格式化字符串添加到全局list中
        :return:
        """
        n_lyrics_lst = len(lyrics_lst)
        idx = 0
        while idx < n_lyrics_lst:
            # Handle phonetic symbols first
            symbols = lyrics_lst[idx]
            idx += 1
            while idx < n_lyrics_lst and (len(symbols) <= 1 or not self._has_numbers(symbols)):
                symbols = lyrics_lst[idx]
                idx += 1
            # Replace specific symbols
            for key in self.replace_dict.keys():
                symbols = symbols.replace(key, self.replace_dict[key])
            # Split
            s_lst = list()
            i_start = 0
            for i in range(len(symbols)):
                if symbols[i].isdigit():
                    s_lst.append(symbols[i_start: i] + '<super>' + symbols[i] + '</super>')
                    i_start = i + 1

            # Handle lyrics second
            words = ''
            if idx < n_lyrics_lst:
                words = lyrics_lst[idx]
                idx += 1
            while idx < n_lyrics_lst and (len(words) <= 1 or not self._has_chinese(words)):
                words = lyrics_lst[idx]
                idx += 1
            w_lst = list(words)

            if len(s_lst) != len(w_lst):
                self._log("PROCESS_ERROR", "Phonetic symbols and text do not match.")
                self._log("ERROR_INFO", "Symbols: " + symbols + ".")
                self._log("ERROR_INFO", "Words: " + words + ".")
                return RTFlag.FAIL

            # Update the max number of cols
            self.max_cols = max(self.max_cols, len(w_lst))
            # Append to global list
            self.output_lst.append(s_lst)
            self.output_lst.append(w_lst)

        return RTFlag.SUCCESS

    @staticmethod
    def _has_numbers(input_string):
        return bool(re.search(r'\d', input_string))

    @staticmethod
    def _has_chinese(input_string):
        return bool(re.search(r'[\u4e00-\u9fa5]+', input_string))

    def _output_to_pdf(self):
        """
        由格式化字符串生成段落，输出为pdf文件
        :return:
        """
        # Config
        stylesheet = getSampleStyleSheet()
        normal_style = stylesheet['Normal']
        title_style = stylesheet['Title']
        pdfmetrics.registerFont(TTFont('SimSun', 'SourceHanSansSC-VF.ttf'))
        normal_style.fontName = 'SimSun'
        title_style.fontName = 'SimSun'

        output_data = list()
        # Title
        output_data.append(Paragraph(self.title, style=title_style))
        # Table Data
        table_data = list()
        for lst in self.output_lst:
            tmp_lst = list()
            for i in range(len(lst)):
                tmp_lst.append(Paragraph(lst[i], style=normal_style))
            for i in range(self.max_cols - len(lst)):
                tmp_lst.append('')
            table_data.append(tmp_lst)
        table_data = Table(table_data)
        table_data.setStyle(TableStyle([('ALIGNMENT', (0, 0), (-1, -1), 'CENTRE')]))
        output_data.append(table_data)

        # output
        doc = SimpleDocTemplate(os.path.join(self.output_file_path, self.title + '.pdf'), pagesize=A4)
        doc.build(output_data)
        return RTFlag.SUCCESS


if __name__ == '__main__':
    cs = CantoScript(regeneration=False)
    cs.start()
