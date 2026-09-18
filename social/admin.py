from django.contrib import admin
from .models import Story,StorySeen,Report,ContentView,Message,DeviceSession,TwoFactorCode,CallSession
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin): list_display=('id','reporter','reason','resolved','created_at'); list_filter=('reason','resolved'); search_fields=('details','reporter__username')
for m in [Story,StorySeen,ContentView,Message,DeviceSession,TwoFactorCode,CallSession]: admin.site.register(m)
