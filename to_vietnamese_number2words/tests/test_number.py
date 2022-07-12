from odoo.tests.common import TransactionCase


class TestNumber2Word(TransactionCase):

    def test_number2words_raises(self):
        with self.assertRaises(Exception):
            self.env['to.vietnamese.number2words'].num2words(12)
        self.assertEqual(
            self.env['to.vietnamese.number2words'].num2words(12, precision_rounding=1),
            'Mười hai'
            )
        self.assertEqual(
            self.env['to.vietnamese.number2words'].num2words(12, precision_digits=0),
            'Mười hai'
            )

    def test_number2words(self):
        num2words = self.env['to.vietnamese.number2words'].num2words
        
        self.assertEqual(num2words(11, precision_rounding=1), 'Mười một', "Converting number 11 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(21, precision_rounding=1), 'Hai mươi mốt', "Converting number 21 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(-52, precision_rounding=1), 'Âm năm mươi hai', "Converting number -52 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(amount=11.256, precision_rounding=0.01), 'Mười một phẩy hai sáu', "Converting number 11.256 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(amount=11.256, precision_rounding=0.001), 'Mười một phẩy hai năm sáu', "Converting number 11.256 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(121, precision_rounding=1), 'Một trăm hai mươi mốt' , "Converting number 121 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(124, precision_rounding=1), 'Một trăm hai mươi bốn' , "Converting number 124 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(1245, precision_rounding=1), 'Một nghìn hai trăm bốn mươi lăm', "Converting number 1245 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(12456, precision_rounding=1), 'Mười hai nghìn bốn trăm năm mươi sáu', "Converting number 12456 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(124567, precision_rounding=1), 'Một trăm hai mươi bốn nghìn năm trăm sáu mươi bảy', "Converting number 124567 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(100011, precision_rounding=1), 'Một trăm nghìn không trăm mười một', "Converting number 100011 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(10000000, precision_rounding=1), 'Mười triệu', "Converting number 10000000 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(400100000, precision_rounding=1), 'Bốn trăm triệu một trăm nghìn', "Converting number 400100000 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(5400100000, precision_rounding=1), 'Năm tỷ bốn trăm triệu một trăm nghìn', "Converting number 5400100000 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(25400100000, precision_rounding=1), 'Hai mươi lăm tỷ bốn trăm triệu một trăm nghìn', "Converting number 25400100000 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(925400100000, precision_rounding=1), 'Chín trăm hai mươi lăm tỷ bốn trăm triệu một trăm nghìn', "Converting number 925400100000 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(amount=0.256, precision_rounding=0.01), 'Không phẩy hai sáu', "Converting number 0.256 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(amount=0.256, precision_rounding=0.001), 'Không phẩy hai năm sáu', "Converting number 0.256 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(amount=-0.256, precision_rounding=0.01), 'Âm không phẩy hai sáu', "Converting number -0.256 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(amount=-0.256, precision_rounding=0.001), 'Âm không phẩy hai năm sáu', "Converting number -0.256 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(amount=1.9999, precision_rounding=0.01), 'Hai', "Converting number 1.9999 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(amount=1.9999, precision_rounding=0.001), 'Hai', "Converting number 1.9999 to word in Vietnamese wasn't correct")
        self.assertEqual(num2words(25500, precision_rounding=1), 'Hai mươi lăm nghìn năm trăm')
        self.assertEqual(num2words(151000, precision_rounding=1), 'Một trăm năm mươi mốt nghìn')
        self.assertEqual(num2words(1500.00, precision_rounding=1), 'Một nghìn năm trăm')
