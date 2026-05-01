from werkzeug.security import check_password_hash
s = 'scrypt:32768:8:1$gntBgY7gPmrvfrt4$f111b0828ec199a950dd513390e71733a9a561741c9f27e56c1534c2431e8596d174666931cc0f5d336adc425fdbdbe5e9ed93531903b0a36188f0afbe5789c2'
print('check', check_password_hash(s, 'admin'))
