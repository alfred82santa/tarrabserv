from django.contrib.admin import ModelAdmin


class CommonAdmin(ModelAdmin):

    class Meta:
        exclude = ('created_by', 'modified_by',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.modified_by = request.user

        super(CommonAdmin, self).save_model(request, obj, form, change)
