from django.conf import settings
if settings.DATABASE_ENGINE=='pool':
	settings.DATABASE_ENGINE=settings.POOL_DATABASE_ENGINE

from django.core.management.base import BaseCommand, CommandError
import os
import time
import sys

class Command(BaseCommand):
	option_list = BaseCommand.option_list + ()
	help = "Starts Sync Queue process."
	args = ''
 
	def handle(self, *args, **options):
		from mysite.iclock.syncqueue import performPostDataFile 
		print self.help
		performPostDataFile(1)

