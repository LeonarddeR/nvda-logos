# NVDA add-on for Logos Bible Study
# Copyright 2024 Leonard de Ruijter <alderuijter@gmail.com>
# License: GNU General Public License version 2.0

import re

import appModuleHandler
import controlTypes
import UIAHandler
from NVDAObjects.UIA import UIA


class UnlabelledElement(UIA):
	name: str

	def _get_name(self):
		match self.role:
			case controlTypes.Role.EDITABLETEXT:
				if self._hintText:
					return self._hintText
			case controlTypes.Role.BUTTON:
				return self.UIAAutomationId

	_hintText: str | None

	def _get__hintText(self):
		childrenCacheRequest = UIAHandler.handler.baseCacheRequest.clone()
		childrenCacheRequest.addProperty(UIAHandler.UIA.UIA_NamePropertyId)
		childrenCacheRequest.TreeScope = UIAHandler.UIA.TreeScope_Children
		childrenCacheRequest.treeFilter = UIAHandler.handler.clientObject.createPropertyCondition(
			UIAHandler.UIA.UIA_AutomationIdPropertyId, "HintText"
		)
		cachedChildren = self.UIAElement.buildUpdatedCache(childrenCacheRequest).getCachedChildren()
		if not cachedChildren:
			return None
		e = cachedChildren.getElement(0)
		return e.cachedName


class BrokenNameElement(UIA):
	_regex = re.compile(r"^\w+\.\w+\.\w+")

	def _get_name(self):
		return self.firstChild.name


class AppModule(appModuleHandler.AppModule):
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if not isinstance(obj, UIA):
			return
		if not obj.name:
			clsList.insert(0, UnlabelledElement)
		elif BrokenNameElement._regex.match(obj.name):
			clsList.insert(0, BrokenNameElement)
