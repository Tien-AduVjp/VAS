from odoo import models
from odoo.tools import float_round
from odoo.tools.float_utils import _float_check_precision


class to_vietnamese_number2words(models.AbstractModel):
    _name = 'to.vietnamese.number2words'
    _description = 'Vietnamese Number to Words'

    def num2words(self, amount, precision_digits=None, precision_rounding=None, rounding_method='HALF-UP'):
        """Method to convert number to words in Vietnamese.
        @amount: number in float type
        """

        rounding_factor = _float_check_precision(
            precision_digits=precision_digits,
            precision_rounding=precision_rounding
            )
        amount = float_round(amount, precision_rounding=rounding_factor, rounding_method=rounding_method)

        if amount == 0:
            return 'Không'

        prefix_word = res = ''
        if amount < 0:
            amount = abs(amount)
            prefix_word += 'Âm '

        # delare
        in_word = ''
        split_mod = ''
        split_remain = ''

        num = int(amount)
        if int(amount) == amount:
            amount = int(amount)

        gnum = str(num)
        gdecimal = str(amount).split('.')[1:]
        if gdecimal:
            gdecimal = gdecimal[0]
        m = len(gnum) // 3
        mod = len(gnum) - m * 3

        # tách hàng lớn nhất
        if mod == 1:
            split_mod = '00' + str(num)[:1]
        elif mod == 2:
            split_mod = '0' + str(num)[:2]
        elif mod == 0:
            split_mod = '000'
        # tách hàng còn lại sau mod
        if len(str(num)) > 2:
            split_remain = str(num)[mod:]
        # đơn vị hàng mod
        im = m + 1
        if mod > 0:
            in_word = self._split_mod(split_mod) + ' ' + self._unit(str(im))
        # tách 3 trong split_remain
        i = m
        _m = m
        j = 1
        split3 = ''
        split3_ = ''
        while i > 0:
            split3 = split_remain[:3]
            split3_ = split3
            in_word = in_word + ' ' + self._split(split3)
            m = _m + 1 - j
            if int(split3_) != 0:
                in_word = in_word + ' ' + self._unit(str(m))
            split_remain = split_remain[3:]
            i = i - 1
            j = j + 1
        if in_word[:1] == 'k':
            in_word = in_word[10:]
        if in_word[:1] == 'l':
            in_word = in_word[2:]
        if len(in_word) > 0:
            in_word = str(in_word.strip()[:1]).upper() + in_word.strip()[1:]

        if gdecimal:
            in_word += ' phẩy'
            for i in range(0, len(gdecimal)):
                in_word += ' ' + self._word(gdecimal[i])

        if num == 0:
            in_word = 'Không ' + in_word[:1].lower() + in_word[1:]
        if prefix_word:
            in_word = prefix_word + in_word[:1].lower() + in_word[1:]

        res = in_word.replace('  ', ' ').strip()
        return res

    def _word(self, number):
        return {
            '0': 'không',
            '1': 'một',
            '2': 'hai',
            '3': 'ba',
            '4': 'bốn',
            '5': 'năm',
            '6': 'sáu',
            '7': 'bảy',
            '8': 'tám',
            '9': 'chín',
        }[number]

    def _unit(self, number_of_digits):
        return {
            '1': '',
            '2': 'nghìn',
            '3': 'triệu',
            '4': 'tỷ',
            '5': 'nghìn',
            '6': 'triệu',
            '7': 'tỷ ',
        }[number_of_digits]

    def _split_mod(self, value):
        res = ''

        if value == '000':
            return ''
        if len(value) == 3:
            tr = value[:1]
            ch = value[1:2]
            dv = value[2:3]
            if tr == '0' and ch == '0':
                res = self._word(dv) + ' '
            if tr != '0' and ch == '0' and dv == '0':
                res = self._word(tr) + ' trăm '
            if tr != '0' and ch == '0' and dv != '0':
                res = self._word(tr) + ' trăm lẻ ' + self._word(dv) + ' '
            if tr == '0' and int(ch) > 1 and int(dv) > 0 and dv != '5':
                if int(dv) == 1:
                    res = self._word(ch) + ' mươi mốt'
                else:
                    res = self._word(ch) + ' mươi ' + self._word(dv)
            if tr == '0' and int(ch) > 1 and dv == '0':
                res = self._word(ch) + ' mươi '
            if tr == '0' and int(ch) > 1 and dv == '5':
                res = self._word(ch) + ' mươi lăm '
            if tr == '0' and ch == '1' and int(dv) > 0 and dv != '5':
                res = ' mười ' + self._word(dv) + ' '
            if tr == '0' and ch == '1' and dv == '0':
                res = ' mười '
            if tr == '0' and ch == '1' and dv == '5':
                res = ' mười lăm '
            if int(tr) > 0 and int(ch) > 1 and int(dv) > 0 and dv != '5':
                if int(dv) == 1:
                    res = self._word(tr) + ' trăm ' + self._word(ch) + ' mươi mốt'
                else:
                    res = self._word(tr) + ' trăm ' + self._word(ch) + ' mươi ' + self._word(dv) + ' '
            if int(tr) > 0 and int(ch) > 1 and dv == '0':
                res = self._word(tr) + ' trăm ' + self._word(ch) + ' mươi '
            if int(tr) > 0 and int(ch) > 1 and dv == '5':
                res = self._word(tr) + ' trăm ' + self._word(ch) + ' mươi lăm '
            if int(tr) > 0 and ch == '1' and int(dv) > 0 and dv != '5':
                res = self._word(tr) + ' trăm mười ' + self._word(dv) + ' '
            if int(tr) > 0 and ch == '1' and dv == '0':
                res = self._word(tr) + ' trăm mười '
            if int(tr) > 0 and ch == '1' and dv == '5':
                res = self._word(tr) + ' trăm mười lăm '

        return res

    def _split(self, value):
        res = ''

        if value == '000':
            return ''
        if len(value) == 3:
            tr = value[:1]
            ch = value[1:2]
            dv = value[2:3]
            if tr == '0' and ch == '0':
                res = ' không trăm lẻ ' + self._word(dv) + ' '
            if tr != '0' and ch == '0' and dv == '0':
                res = self._word(tr) + ' trăm '
            if tr != '0' and ch == '0' and dv != '0':
                res = self._word(tr) + ' trăm lẻ ' + self._word(dv) + ' '
            if tr == '0' and int(ch) > 1 and int(dv) > 0 and dv != '5':
                if int(dv) == 1:
                    res = ' không trăm ' + self._word(ch) + ' mươi mốt'
                else:
                    res = ' không trăm ' + self._word(ch) + ' mươi ' + self._word(dv)
            if tr == '0' and int(ch) > 1 and dv == '0':
                res = ' không trăm ' + self._word(ch) + ' mươi '
            if tr == '0' and int(ch) > 1 and dv == '5':
                res = ' không trăm ' + self._word(ch) + ' mươi lăm '
            if tr == '0' and ch == '1' and int(dv) > 0 and dv != '5':
                res = ' không trăm mười ' + self._word(dv)
            if tr == '0' and ch == '1' and dv == '0':
                res = ' không trăm mười '
            if tr == '0' and ch == '1' and dv == '5':
                res = ' không trăm mười lăm '
            if int(tr) > 0 and int(ch) > 1 and int(dv) > 0 and dv != '5':
                if int(dv) == 1:
                    res = self._word(tr) + ' trăm ' + self._word(ch) + ' mươi mốt'
                else:
                    res = self._word(tr) + ' trăm ' + self._word(ch) + ' mươi ' + self._word(dv) + ' '
            if int(tr) > 0 and int(ch) > 1 and dv == '0':
                res = self._word(tr) + ' trăm ' + self._word(ch) + ' mươi '
            if int(tr) > 0 and int(ch) > 1 and dv == '5':
                res = self._word(tr) + ' trăm ' + self._word(ch) + ' mươi lăm '
            if int(tr) > 0 and ch == '1' and int(dv) > 0 and dv != '5':
                res = self._word(tr) + ' trăm mười ' + self._word(dv) + ' '
            if int(tr) > 0 and ch == '1' and dv == '0':
                res = self._word(tr) + ' trăm mười '
            if int(tr) > 0 and ch == '1' and dv == '5':
                res = self._word(tr) + ' trăm mười lăm '

        return res
