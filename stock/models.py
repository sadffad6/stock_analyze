from django.db import models

class Stock(models.Model):
    """股票数据模型，包含基本交易信息和技术指标"""
    # 品牌字段作为主键
    brand = models.CharField(
        max_length=100,
        verbose_name="品牌"
    )
    # 股票代码
    code = models.CharField(
        max_length=20,
        verbose_name="股票代码"
    )
    # 股票名称
    name = models.CharField(
        max_length=100,
        verbose_name="股票名称"
    )
    # 日期
    date = models.DateField(
        verbose_name="日期"
    )
    # 开盘价
    open = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="开盘价"
    )
    # 收盘价
    close = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="收盘价"
    )
    # 最高价
    high = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="最高价"
    )
    # 最低价
    low = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="最低价"
    )
    # 成交量
    volume = models.BigIntegerField(
        verbose_name="成交量"
    )
    # 成交额
    turnover = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        verbose_name="成交额"
    )
    # 振幅
    amplitude = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="振幅(%)"
    )
    # 涨跌幅
    change_pct = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="涨跌幅(%)"
    )
    # 涨跌额
    change_amt = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="涨跌额"
    )
    # 换手率
    turnover_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="换手率(%)"
    )

    class Meta:
        verbose_name = "股票数据"
        verbose_name_plural = "股票数据"
        # 可以根据需要添加联合索引，例如按品牌和日期查询
        indexes = [
            models.Index(fields=['brand', 'date']),
            models.Index(fields=['code', 'date']),
        ]
        # 确保同一品牌在同一天只有一条记录
        unique_together = ['brand', 'date']

    def __str__(self):
        return f"{self.brand}({self.code})-{self.date}"

