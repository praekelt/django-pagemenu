from datetime import datetime, timedelta

from django.conf import settings
from django.core.urlresolvers import RegexURLResolver, Resolver404
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str

from secretballot.models import Vote

class Item(object):
    def __init__(self, request, title, default):
        self.request=request
        self.title=title
        self.default=default
            
class GetItem(Item):
    def __init__(self, request, title, get, field_name='', default=False):
        get['value'] = str(get['value'])
        self.get=get
        self.field_name = field_name
        super(GetItem, self).__init__(request, title, default)

    def is_active(self, request):
        if hasattr(self, 'get'):
            if request.GET.has_key(self.get['name']):
                return request.GET[self.get['name']] == self.get['value']

        return False
    
    def get_absolute_url(self):
        addition_pairs = [(self.get['name'], self.get['value']),]
        remove_keys = ['page', ]
        q = dict([(k, v) for k, v in self.request.GET.items()])
        for key in remove_keys:
            if q.has_key(key):
                del q[key]
        for key, value in addition_pairs:
            if key:
                if value:
                   q[key] = value
                else:
                    q.pop(key, None)
            qs = '&'.join(['%s=%s' % (k, v) for k, v in q.items()])
        return '?' + qs if len(q) else ''

class IntegerFieldRangeItem(GetItem):
    def __init__(self, request, title, get, field_name, filter_range, default=False):
        self.field_name = field_name
        self.filter_range = filter_range
        super(IntegerFieldRangeItem, self).__init__(request, title, get, field_name, default)

    def action(self, queryset):
        return queryset.filter(**{"%s__range" % self.field_name: self.filter_range})

class URLPatternItem(Item):
    def __init__(self, request, title, path, matching_pattern_names, default):
        self.path = path
        self.matching_pattern_names = matching_pattern_names
        super(URLPatternItem, self).__init__(request, title, default)
    
    def resolve_pattern_name(self, resolver, path):
        tried = []
        match = resolver.regex.search(path)
        if match:
            new_path = path[match.end():]
            for pattern in resolver.url_patterns:
                try:
                    sub_match = pattern.resolve(new_path)
                except Resolver404, e:
                    sub_tried = e.args[0].get('tried')
                    if sub_tried is not None:
                        tried.extend([(pattern.regex.pattern + '   ' + t) for t in sub_tried])
                    else:
                        tried.append(pattern.regex.pattern)
                else:
                    if sub_match:
                        sub_match_dict = dict([(smart_str(k), v) for k, v in match.groupdict().items()])
                        sub_match_dict.update(resolver.default_kwargs)
                        for k, v in sub_match[2].iteritems():
                            sub_match_dict[smart_str(k)] = v
                        try:
                            return pattern.name
                        except AttributeError:
                            return self.resolve_pattern_name(pattern, new_path)
                    tried.append(pattern.regex.pattern)
            raise Resolver404, {'tried': tried, 'path': new_path}
        raise Resolver404, {'path' : path}
    
    def is_active(self, request):
        urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
        resolver = RegexURLResolver(r'^/', urlconf)

        url_name = self.resolve_pattern_name(resolver, request.path)
        return url_name in self.matching_pattern_names

    def action(self, queryset):
        return queryset

    def get_absolute_url(self):
        return self.path

class MostRecentItem(GetItem):
    def action(self, queryset):
        return queryset.order_by('-%s' % self.field_name)

class MostLikedItem(GetItem):
    def action(self, queryset):
        return queryset.extra(select={
                'vote_score': '(SELECT COUNT(*) from %s WHERE vote=1 AND object_id=%s.%s AND content_type_id=%s) - (SELECT COUNT(*) from %s WHERE vote=-1 AND object_id=%s.%s AND content_type_id=%s)' % (Vote._meta.db_table, queryset.model._meta.db_table, queryset.model._meta.pk.attname, ContentType.objects.get_for_model(queryset.model).id, Vote._meta.db_table, queryset.model._meta.db_table, queryset.model._meta.pk.attname, ContentType.objects.get_for_model(queryset.model).id)}).order_by('-vote_score')

class ThisWeekItem(GetItem):
    def action(self, queryset):
        return queryset.filter(**{
            '%s__gte' % self.field_name: (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
            '%s__lt' % self.field_name: (datetime.today()+timedelta(days=1)).strftime('%Y-%m-%d'),
        })
        
class ThisWeekendItem(GetItem):
    def action(self, queryset):
        return queryset.filter(**{
            '%s__gte' % self.field_name: (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
            '%s__lt' % self.field_name: (datetime.today()+timedelta(days=1)).strftime('%Y-%m-%d'),
        })

class ThisMonthItem(GetItem):
    def action(self, queryset):
        return queryset.filter(**{
            '%s__year' % self.field_name: datetime.today().year,
            '%s__month' % self.field_name: datetime.today().month
        })
