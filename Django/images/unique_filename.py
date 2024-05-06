def unique_filename(path):
    """
    Enforce unique upload file names.
    Usage:
    class MyModel(models.Model):
        file = ImageField(upload_to=unique_filename("path/to/upload/dir"))
    """
    import os, base64, datetime
    def _func(instance, filename):
        name, ext = os.path.splitext(filename)
        name = base64.urlsafe_b64encode(name.encode("utf-8") + str(datetime.datetime.now()))
        return os.path.join(path, name + ext)
    return _func
