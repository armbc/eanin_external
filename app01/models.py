from django.db import models


class Admin(models.Model):
    """ 管理员表 """
    username = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=64)


class Department(models.Model):
    """ 部门表 """
    name = models.CharField(verbose_name='部门名称', max_length=32)
    area = models.CharField(verbose_name='所属区域', max_length=64)

    def __str__(self):
        return self.name


class User(models.Model):
    """ 员工表 """
    name = models.CharField(verbose_name='姓名', max_length=16)
    gender_choices = (
        (1, "男"),
        (2, "女"),
    )
    gender = models.SmallIntegerField(verbose_name='性别', choices=gender_choices)
    password = models.CharField(verbose_name='密码', max_length=64)
    create_time = models.DateField(verbose_name='入职时间')
    quit_time = models.DateField(verbose_name='离职时间', null=True, blank=True)
    depart = models.ForeignKey(verbose_name='部门', to='Department', to_field='id', null=True, blank=True,
                               on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Material(models.Model):
    """ 物料表 """
    name = models.CharField(verbose_name='名称', max_length=32)
    category_choices = (
        (1, "原辅料"),
        (2, "包装材料"),
        (3, "半成品"),
        (4, "产成品"),
        (5, "外购商品"),
        (6, "办公用品"),
        (7, "设备"),
    )
    category = models.SmallIntegerField(verbose_name='类别', choices=category_choices)
    model = models.CharField(verbose_name='型号', max_length=64, null=True, blank=True)
    unit = models.CharField(verbose_name='计量单位', max_length=64)
    guarantee_period = models.IntegerField(verbose_name='保质期')

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """ 供应商表 """
    name = models.CharField(verbose_name='名称', max_length=32)
    address = models.CharField(verbose_name='地址', max_length=64)
    phone = models.CharField(verbose_name='电话', max_length=32)

    def __str__(self):
        return self.name


class Warehousing(models.Model):
    """ 入库表 """
    warehousing_name = models.ForeignKey(verbose_name='名称', to='Material', to_field='id', null=True, blank=True,
                                         on_delete=models.SET_NULL)
    supplier = models.ForeignKey(verbose_name='供应商', to='Supplier', to_field='id', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    warehousing_date = models.DateField(verbose_name='入库时间', null=True, blank=True)
    quantity = models.DecimalField(verbose_name='数量', max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(verbose_name='单价', max_digits=10, decimal_places=2)
    price = models.DecimalField(verbose_name='金额', max_digits=12, decimal_places=2)
    operator = models.ForeignKey(verbose_name='操作员', to='User', to_field='id', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    approved_choices = (
        (0, '未审核'),
        (1, '已审核'),
    )
    approved = models.SmallIntegerField(verbose_name='审核', choices=approved_choices)
    produceDate = models.DateField(verbose_name='生产日期', null=True, blank=True)
    closingDate = models.DateField(verbose_name='截止日期', null=True, blank=True)
    batchCode = models.CharField(verbose_name='批次编码', max_length=32, null=True, blank=True)
    surplus = models.DecimalField(verbose_name='剩余数量', max_digits=10, decimal_places=2)

    def __str__(self):
        return self.warehousing_name


class Inventory(models.Model):
    """ 盘点表 """
    inventoryDate = models.DateField(verbose_name='盘点日期')
    name = models.ForeignKey(verbose_name='名称', to='Material', to_field='id', null=True, blank=True,
                             on_delete=models.SET_NULL)
    inventoryQuantity = models.DecimalField(verbose_name='盘点数量', max_digits=10, decimal_places=2)
    bookQuantity = models.DecimalField(verbose_name='账面数量', max_digits=10, decimal_places=2)
    bookAmount = models.DecimalField(verbose_name='库存金额', max_digits=12, decimal_places=2, null=True, blank=True)
    errorsNumber = models.DecimalField(verbose_name='误差数量', max_digits=10, decimal_places=2)
    errorsAmount = models.DecimalField(verbose_name='误差金额', max_digits=12, decimal_places=2)
    operator = models.ForeignKey(verbose_name='操作员', to='User', to_field='id', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    approved_choices = (
        (0, '未审核'),
        (1, '已审核'),
    )
    approved = models.SmallIntegerField(verbose_name='审核', choices=approved_choices)

    def __str__(self):
        return self.name


# class issueUnitPrice(models.Model):
#     """ 出库单价 """
#     date = models.DateField(verbose_name='日期', null=True, blank=True)
#     name = models.ForeignKey(verbose_name='名称', to='Material', to_field='id', null=True, blank=True,
#                              on_delete=models.SET_NULL)
#     issueUnitPrice = models.DecimalField(verbose_name='出库单价', max_digits=12, decimal_places=2)
#
#     def __str__(self):
#         return self.name


class outbound(models.Model):
    """ 出库表 """
    batchCode = models.CharField(verbose_name='批次编码', max_length=32)
    date = models.DateField(verbose_name='日期', null=True, blank=True)
    department = models.ForeignKey(verbose_name='领取部门', to='Department', to_field='id', null=True, blank=True,
                                   on_delete=models.SET_NULL)
    name = models.ForeignKey(verbose_name='名称', to='Material', to_field='id', null=True, blank=True,
                             on_delete=models.SET_NULL)
    outbound = models.DecimalField(verbose_name='出库数量', max_digits=10, decimal_places=2)
    issueAmount = models.DecimalField(verbose_name='出库金额', max_digits=12, decimal_places=2)
    issueUnitPrice = models.DecimalField(verbose_name='出库单价', max_digits=12, decimal_places=2)
    operator = models.ForeignKey(verbose_name='操作员', to='User', to_field='id', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    approved_choices = (
        (0, '未审核'),
        (1, '已审核'),
    )
    approved = models.SmallIntegerField(verbose_name='审核', choices=approved_choices)

    def __str__(self):
        return self.name
