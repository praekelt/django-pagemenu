from django.conf import settings
from django.core.urlresolvers import RegexURLResolver, Resolver404
from django.utils.encoding import smart_str

class Item(object):
    def __init__(self, request, title, default):
        self.request=request
        self.title=title
        self.default=default
            
class GetItem(Item):
    def __init__(self, request, title, get, default):
        get['value'] = str(get['value'])
        self.get=get
        super(GetItem, self).__init__(request, title, default)

    def is_active(self, request):
        if hasattr(self, 'get'):
            if request.GET.has_key(self.get['name']):
                return request.GET[self.get['name']] == self.get['value']

        return False

class IntegerFieldRangeItem(GetItem):
    def __init__(self, title, get, field_name, filter_range, default=False):
        self.field_name = field_name
        self.filter_range = filter_range
        super(IntegerFieldRangeItem, self).__init__(title, get, default)

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
