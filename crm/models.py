from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Customer(models.Model):
    '''客户表'''
    name = models.CharField(max_length=32, blank=True, null=True)
    qq = models.CharField(max_length=64, unique=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    source_choices = ((0, '转介绍'),
                     (1, 'QQ群'),
                     (2, '官网'),
                     (3, '百度推广'),
                     (4, '51CTO'),
                     (5, '知乎'),
                     (6, '市场推广'),
                     )
    source = models.SmallIntegerField(choices=source_choices)
    referral_from = models.CharField(verbose_name="转介绍人QQ", max_length=64, blank=True, null=True)
    consult_course = models.ForeignKey("Course", verbose_name="咨询课程")  # 外键，关联Course表
    content = models.TextField(verbose_name="咨询详情")
    consultant = models.ForeignKey("UserProfile")
    # 备注 可以不写
    note = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.qq

class Tag(models.Model):
    name = models.CharField(unique=True, max_length=32)

    def __str__(self):
        return self.name


class CustomerFollowUp(models.Model):
    '''客户跟进表'''
    customer = models.ForeignKey("Customer")
    content = models.TextField(verbose_name="跟进内容")
    consultant = models.ForeignKey("UserProfile")
    intention_choices = ((0, '2周内报名'),
                         (1, '1个月内报名'),
                         (2, '近期无报名计划'),
                         (3, '已在其他机构报名'),
                         (4, '已报名'),
                         (5, '已拉黑')
                         )
    # 报名意向
    intention = models.SmallIntegerField(choices=intention_choices)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<%s: %s>" % (self.customer.qq, self.intention)


class Course(models.Model):
    '''课程表'''
    name = models.CharField(max_length=64, unique=True)
    price = models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name="周期(月)")
    outline = models.TextField()

    def __str__(self):
        return self.name


class Branch(models.Model):
    '''校区'''
    name = models.CharField(max_length=128, unique=True)
    addr = models.CharField(max_length=128)



class ClassList(models.Model):
    '''班级表'''
    branch = models.ForeignKey("Branch")  # 校区
    course = models.ForeignKey("Course")
    semester = models.PositiveSmallIntegerField(verbose_name="学期")
    teachers = models.ManyToManyField("UserProfile")
    class_type_choices = ((0, "面授(脱产)"),
                          (1, "面授(周末)"),
                          (2, "网络班")
                          )
    class_type = models.ManyToManyField("UserProfile")
    start_date = models.DateField(verbose_name="开班日期")
    end_date = models.DateField(verbose_name="结业日期", blank=True, null=True)

    def __str__(self):
        return "<%s: %s: %s>" % (self.branch, self.course, self.semester)

    class Meta:
        # 联合唯一
        unique_together = ("branch", "course", "semester")


class CourseRecord(models.Model):
    '''上课记录表'''
    from_class = models.ForeignKey("ClassList", verbose_name="班级")
    day_num = models.PositiveSmallIntegerField(verbose_name="课节(天)")
    teacher = models.ForeignKey("UserProfile")
    has_homework = models.BooleanField(default=True)
    homework_title = models.CharField(max_length=128, blank=True, null=True)
    homework_content = models.TextField(blank=True, null=True)
    outline = models.TextField(verbose_name="本节课程大纲")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "<%s: %s>" % (self.from_class, self.day_num)

    class Meta:
        unique_together = ("from_class", "day_num")


class StudyRecord(models.Model):
    '''学习记录表'''
    student = models.ForeignKey("Enrollment")
    # 上课记录
    course_record = models.ForeignKey("CourseRecord")
    attendance_choices = ((0, '已签到'),
                          (0, '迟到'),
                          (0, '缺勤'),
                          (0, '早退')
                          )
    attendance = models.SmallIntegerField(choices=attendance_choices, default=0)
    score_choices = ((100, 'A+'),
                     (90, 'A'),
                     (85, 'B+'),
                     (80, 'B'),
                     (75, 'B-'),
                     (70, 'C+'),
                     (60, 'C'),
                     (40, 'C-'),
                     (-50, 'D'),
                     (-100, 'COPY'),
                     (0, 'N/A'))
    score = models.SmallIntegerField(choices=score_choices)
    memo = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "<%s: %s: %s>" % (self.student, self.course_record, self.score)


class Enrollment(models.Model):
    '''报名表'''
    customer = models.ForeignKey("Customer")
    enrolled_class = models.ForeignKey("ClassList", verbose_name="所报班级")
    consultant = models.ForeignKey("UserProfile", verbose_name="课程顾问")
    contract_agreed = models.BooleanField(default=False, verbose_name="学院已同意合同")
    contract_approved = models.BooleanField(default=False, verbose_name="合同已审核")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<%s: %s>" % (self.customer, self.enrolled_class)

    class Meta:
        unique_together = ("customer", "enrolled_class")


class Pyament(models.Model):
    '''缴费记录'''
    customer = models.ForeignKey("Customer")
    course = models.ForeignKey("Course", verbose_name="所报课程")
    amount = models.PositiveIntegerField(verbose_name="数额", default=500)
    consultant = models.ForeignKey("UserProfile")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<%s: %s: %s>" % (self.customer, self.course, self.amount)


class UserProfile(models.Model):
    '''账号表'''
    user = models.OneToOneField(User)
    name = models.CharField(max_length=32)
    roles = models.ManyToManyField("Role", blank=True, null=True)

    def __str__(self):
        return "<%s>" % self.name


class Role(models.Model):
    '''角色表'''
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return "<%s>" % (self.name)



