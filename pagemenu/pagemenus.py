from items import IntegerFieldRangeItem

class PageMenu(object):
    def __init__(self, queryset, request):
        self.queryset = queryset
        self.request = request
        self.active_items = self.get_active_items()

        for item in self.active_items:
            self.queryset = item.action(self.queryset)

    def get_active_items(self):
        active_items = []
        for item in self.items:
            if hasattr(item, 'get'):
                if self.request.GET.has_key(item.get['name']):
                    if self.request.GET[item.get['name']] == item.get['value']:
                         active_items.append(item)
        
        if not active_items:
            for item in self.items:
                if item.default:
                    active_items.append(item)
        
        return active_items

class IntegerFieldRangePageMenu(PageMenu):
    def __init__(self, queryset, request, field_name, interval):
        self.items = []

        ranges = range(0, queryset.count(), interval)
        i = 0
        for range_start in ranges:
            range_end = range_start + interval
            range_start = range_start + 1
            self.items.append(IntegerFieldRangeItem(
                title="%s-%s" % (range_start, range_end),
                field_name=field_name,
                filter_range=(range_start, range_end),
                get={'name': 'range', 'value': range_start},
                default=i==0,
            ))
            i += 1

        super(IntegerFieldRangePageMenu, self).__init__(queryset, request)
