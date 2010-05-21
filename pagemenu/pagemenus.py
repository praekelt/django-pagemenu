from items import IntegerFieldRangeItem, CalEntryNext7DaysItem, CalEntryThisWeekendItem, CalEntryThisMonthItem, CalEntryUpcomingItem

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
            if item.is_active(self.request):
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
                request=request,
                title="%s-%s" % (range_start, range_end),
                get={'name': 'range', 'value': range_start},
                field_name=field_name,
                filter_range=(range_start, range_end),
                default=i==0,
            ))
            i += 1

        super(IntegerFieldRangePageMenu, self).__init__(queryset, request)

class DateFieldIntervalPageMenu(PageMenu):
    def __init__(self, queryset, request, field_name):
        self.items = [
            CalEntryUpcomingItem(
                request=request,
                title="Upcoming",
                get={'name': 'filter', 'value': 'recent'},
                field_name=field_name,
                default=True,
            ), 
            CalEntryThisWeekendItem(
                request=request,
                title="This Weekend",
                get={'name': 'filter', 'value': 'weekend'},
                field_name=field_name,
            ), 
            CalEntryNext7DaysItem(
                request=request,
                title="Next 7 Days",
                get={'name': 'filter', 'value': 'week'},
                field_name=field_name,
            ), 
            CalEntryThisMonthItem(
                request=request,
                title="This Month",
                get={'name': 'filter', 'value': 'month'},
                field_name=field_name,
            ), 
        ]
        
        super(DateFieldIntervalPageMenu, self).__init__(queryset, request)
