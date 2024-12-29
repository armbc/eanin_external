"""
MD5加盐（Django的随机字符串）加秘密
-------------------------------------------------------------------------
'123' -> f818c1869bff49b7b8e5061949e621ed
'123456' -> b6e1e17859c39a60d8d7cc02c5f565ab

                ********** 在MySQL中，修改密码：**********

insert into app01_admin(username,password) values('马秉成123','f818c1869bff49b7b8e5061949e621ed');

insert into app01_user(name,gender,password,create_time,quit_time,depart_id) values
    -> ('马秉成',1,'b6e1e17859c39a60d8d7cc02c5f565ab','1993-10-09',NULL,NULL);
-------------------------------------------------------------------------
DELL H笔记本：
b1b3f41638dee89db39743d838423ced
aa895453c8e061d36e4592ae00288014
"""
from django.conf import settings
import hashlib


def md5(data_string):
    # sold = settings.SECRET_KEY
    sold = 'django-insecure-ce66#u&3$g3gr!%at9r6-36247$au)rlv^qlgg&*96%$ya!jlt'
    obj = hashlib.md5(sold.encode('utf-8'))
    obj.update(data_string.encode('utf-8'))
    return obj.hexdigest()


pwd = '123456'
mped = md5(pwd)
print(mped)  # ae23c4e339ca087f11b0145624160f25
