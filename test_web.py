#!/usr/bin/env python

MSG=file('msg.txt', 'r').read()
TITLE="Title: " + MSG

file('test.html', 'w').write('''
<html>
<head>
<title>%s</title>
</head>
<body>
<center>
<H1>%s</H1>
</center>
</body>
</html>
''' % (TITLE, MSG))

MSG=int(MSG) + 1
file('msg.txt', 'w').write(str(MSG))

