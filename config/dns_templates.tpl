#以下均为 DNS 配置文件，使用 jinja2 来渲染配置文件，然后推送到etcd服务器上

VIEW_DEFINE_TEMPLATE = '''
{% for view in view_list -%}
include "/etc/named/{{ view.name }}/view.conf";
include "/etc/named/{{ view.name }}/acl.conf";
{% endfor %}
'''


ACL_TEMPLATE = ''' 
acl "{{ view_name }}" {
{% for ip in ip_list -%}
{{ ip }};
{% endfor %}
};
'''


VIEW_TEMPLATE = '''
view "{{ view_name }}" {
    match-clients { key default; "{{ view_name }}"; };
 
    zone "." IN {
            type hint;
            file "named.ca";
    };
};
'''


ZONE_TEMPLATE = '''
view "{{ view_name }}" {
    match-clients { key default; "{{ view_name }}"; };
 
    zone "." IN {
            type hint;
            file "named.ca";
    };
 
{% for zone in zone_list %}
    zone "{{ zone.name }}" IN {
            {% if zone.zone_type == 'forward only' %}
            type forward;
            forward only;
            forwarders { {{ zone.forwarders }} };
            {% else %}
            type {{ zone.zone_type }};
            file "zone/{{ view_name }}/zone.{{ zone.name }}";
            notify yes;
            {% endif %}
    };
{% endfor %}
};
'''


RECORD_TEMPLATE = '''
$ORIGIN .
$TTL 600    ; 10 minutes
{{ zone_name }}        IN SOA  master.{{ zone_name }}. root.{{ zone_name }}. (
                2015081304 ; serial
                10800      ; refresh (3 hours)
                900        ; retry (15 minutes)
                604800     ; expire (1 week)
                86400      ; minimum (1 day)
                )
            MX  10 master.{{ zone_name }}.
$ORIGIN {{ zone_name }}.
 
@    86400    IN    NS    master.{{ zone_name }}.
{% for record in record_list -%}
{{ record.host }}    {{ record.ttl }}    IN    {{ record.record_type }}    {{ record.value }}
{% endfor %}
'''


