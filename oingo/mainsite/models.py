from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    nid = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    ntext = models.CharField(max_length=500)
    lat = models.DecimalField(max_digits=14, decimal_places=10)
    lng = models.DecimalField(max_digits=14, decimal_places=10)
    radius = models.FloatField()
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    scheduletype = models.IntegerField()
    visibility = models.IntegerField()
    createtime = models.DateTimeField()


class Friend(models.Model):
    friender = models.IntegerField()
    friendee = models.IntegerField()
    confirmed = models.BooleanField()
    createtime = models.DateTimeField()


class Comment(models.Model):
    cid = models.AutoField(primary_key=True)
    ctext = models.CharField(max_length=500)
    createtime = models.DateTimeField()
    nid = models.ForeignKey(Note, on_delete=models.CASCADE)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)


class Tag(models.Model):
    tid = models.AutoField(primary_key=True)
    ttext = models.CharField(max_length=50)


class NoteTag(models.Model):
    nid = models.ForeignKey(Note, on_delete=models.CASCADE)
    tid = models.ForeignKey(Tag, on_delete=models.CASCADE)


class State(models.Model):
    sid = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    stext = models.CharField(max_length=50)


class Location(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    ltime = models.DateTimeField()
    lat = models.DecimalField(max_digits=14, decimal_places=10)
    lng = models.DecimalField(max_digits=14, decimal_places=10)
    sid = models.ForeignKey(State, on_delete=models.CASCADE)
    operation = models.CharField(max_length=50)


class Filter(models.Model):
    fid = models.AutoField(primary_key=True)
    lat = models.DecimalField(max_digits=14, decimal_places=10)
    lng = models.DecimalField(max_digits=14, decimal_places=10)
    radius = models.FloatField()
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    onfriend = models.IntegerField()
    tid = models.ForeignKey(Tag, on_delete=models.CASCADE)
    sid = models.ForeignKey(State, on_delete=models.CASCADE)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
