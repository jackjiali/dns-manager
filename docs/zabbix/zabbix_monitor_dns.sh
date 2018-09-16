#!/bin/bash
named_stats='/tmp/named_stats.txt'
###++ Incoming Requests ++
Incoming_QUERY=`awk '/QUERY/{print $1}' $named_stats`
Incoming_RESERVED9=`awk '/RESERVED9/{print $1}' $named_stats`
###++ Incoming Queries ++
Incoming_A=`grep A $named_stats |awk 'NR==1{print $1}'`
Incoming_SOA=`grep SOA $named_stats |awk 'NR==1{print $1}'`
Incoming_PTR=`grep PTR $named_stats |awk 'NR==1{print $1}'`
Incoming_MX=`grep MX $named_stats |awk 'NR==1{print $1}'`
Incoming_TXT=`grep TXT $named_stats |awk 'NR==1{print $1}'`
Incoming_AAAA=`grep AAAA $named_stats |awk 'NR==1{print $1}'`
Incoming_A6=`grep A6 $named_stats |awk 'NR==1{print $1}'`
Incoming_IXFR=`grep IXFR $named_stats |awk 'NR==1{print $1}'`
Incoming_ANY=`grep ANY $named_stats |awk 'NR==1{print $1}'`
###++ Outgoing Queries ++
Outgoing_A=`grep  "\<A\>" $named_stats |awk 'NR==2{print $1}'`
Outgoing_NS=`grep NS $named_stats |awk 'NR==1{print $1}'`
Outgoing_PTR=`grep PTR $named_stats |awk 'NR==2{print $1}'`
#Outgoing_AAAA=`grep NS $named_stats |awk 'NR==2{print $1}'`
Outgoing_DNSKEY=`grep DNSKEY $named_stats |awk 'NR==1{print $1}'`
Outgoing_ANY=`grep ANY $named_stats |awk 'NR==2{print $1}'`
Outgoing_DLV=`grep DLV $named_stats |awk 'NR==2{print $1}'`
###++ Name Server Statistics ++
Statistics_IPv4_requests=`grep "IPv4 requests received" $named_stats |awk 'NR==1{print $1}'`
Statistics_requests_received=`grep "requests with EDNS(0) received" $named_stats |awk 'NR==1{print $1}'`
Statistics_TCP_requests=`grep "TCP requests received" $named_stats |awk 'NR==1{print $1}'`
Statistics_queries_rejected=`grep "recursive queries rejected" $named_stats |awk 'NR==1{print $1}'`
Statistics_responses_sent=`grep "responses sent" $named_stats |awk 'NR==1{print $1}'`
Statistics_EDNS_sent=`grep "responses with EDNS(0) sent" $named_stats |awk 'NR==1{print $1}'`
Statistics_successful_answer=`grep "queries resulted in successful answer" $named_stats |awk 'NR==1{print $1}'`
Statistics_authoritative_answer=`grep "queries resulted in authoritative answer" $named_stats |awk 'NR==1{print $1}'`
Statistics_non_authoritative_answer=`grep "queries resulted in non authoritative answer" $named_stats |awk 'NR==1{print $1}'`
Statistics_nxrrset=`grep "queries resulted in nxrrset" $named_stats |awk 'NR==1{print $1}'`
Statistics_SERVFAIL=`grep "queries resulted in SERVFAIL" $named_stats |awk 'NR==1{print $1}'`
Statistics_NXDOMAIN=`grep "queries resulted in NXDOMAIN" $named_stats |awk 'NR==1{print $1}'`
Statistics_recursion=`grep "queries resulted in recursion" $named_stats |awk 'NR==1{print $1}'`
Statistics_received=`grep "queries resulted in received" $named_stats |awk 'NR==1{print $1}'`
Statistics_dropped=`grep "queries resulted in dropped" $named_stats |awk 'NR==1{print $1}'`
###++ Resolver Statistics ++
Resolver_sent=`grep "IPv4 queries sent" $named_stats |awk 'NR==1{print $1}'`
Resolver_received=`grep "IPv4 responses received" $named_stats |awk 'NR==1{print $1}'`
#Resolver_NXDOMAIN_received=`grep "" $named_stats |awk 'NR==1{print $1}'`
#Resolver_responses_received=`sed -n '49p' $named_stats |sed 's/^[ \t]*//g'|cut -d ' ' -f 1`
#Resolver_delegations_received=`sed -n '50p' $named_stats |sed 's/^[ \t]*//g'|cut -d ' ' -f 1`
Resolver_query_retries=`grep "query retries" $named_stats |awk 'NR==1{print $1}'`
Resolver_query_timeouts=`grep "query timeouts" $named_stats |awk 'NR==1{print $1}'`
Resolver_fetches=`grep "IPv4 NS address fetches" $named_stats |awk 'NR==1{print $1}'`
#Resolver_fetch_failed=`sed -n '54p' $named_stats |sed 's/^[ \t]*//g'|cut -d ' ' -f 1`
Resolver_validation_attempted=`grep "DNSSEC validation attempted" $named_stats |awk 'NR==1{print $1}'`
Resolver_validation_succeeded=`grep "DNSSEC validation succeeded" $named_stats |awk 'NR==1{print $1}'`
Resolver_NX_validation_succeeded=`grep "DNSSEC NX validation succeeded" $named_stats |awk 'NR==1{print $1}'`
Resolver_RTT_10ms=`grep "queries with RTT < 10ms" $named_stats |awk 'NR==1{print $1}'`
Resolver_RTT_100ms=`grep "queries with RTT 10-100ms" $named_stats |awk 'NR==1{print $1}'`
Resolver_RTT_500ms=`grep "queries with RTT 100-500ms" $named_stats |awk 'NR==1{print $1}'`
Resolver_RTT_800ms=`grep "queries with RTT 500-800ms" $named_stats |awk 'NR==1{print $1}'`
Resolver_RTT_1600ms=`grep "queries with RTT 800-1600ms" $named_stats |awk 'NR==1{print $1}'`
#Resolver_RTT_gt_1600ms=`sed -n '63p' $named_stats |sed 's/^[ \t]*//g'|cut -d ' ' -f 1`
###++ Cache DB RRsets ++
Cache_A=`grep  "\<A\>" $named_stats |awk 'NR==3{print $1}'`
Cache_NS=`grep  "\<NS\>" $named_stats |awk 'NR==3{print $1}'`
#Cache_CNAME=`sed -n '69p' $named_stats |sed 's/^[ \t]*//g'|cut -d ' ' -f 1`
#Cache_SOA=`sed -n '70p' $named_stats |sed 's/^[ \t]*//g'|cut -d ' ' -f 1`
#Cache_PTR=`sed -n '71p' $named_stats |sed 's/^[ \t]*//g'|cut -d ' ' -f 1`
Cache_AAAA=`grep  "\<AAAA\>" $named_stats |awk 'NR==2{print $1}'`
Cache_DS=`grep "DS" $named_stats |awk 'NR==1{print $1}'`
Cache_RRSIG=`grep "RRSIG" $named_stats |awk 'NR==1{print $1}'`
Cache_NSEC=`grep "NSEC" $named_stats |awk 'NR==1{print $1}'`
Cache_DNSKEY=`grep "DNSKEY" $named_stats |awk 'NR==2{print $1}'`
#Cache_AAA=`sed -n '77p' $named_stats |sed 's/^[ \t]*//g'|cut -d ' ' -f 1`
Cache_cDLV=`grep "DLV" $named_stats |awk 'NR==2{print $1}'`
#Cache_NXDOMAIN=`sed -n '79p' $named_stats |sed 's/^[ \t]*//g'|cut -d ' ' -f 1`
###++ Socket I/O Statistics ++
Socket_UDP_opened=`grep "UDP/IPv4 sockets opened" $named_stats |awk 'NR==1{print $1}'`
Socket_TCP_opened=`grep "TCP/IPv4 sockets opened" $named_stats |awk 'NR==1{print $1}'`
Socket_UDP_closed=`grep "UDP/IPv4 sockets closed" $named_stats |awk 'NR==1{print $1}'`
Socket_TCP_closed=`grep " TCP/IPv4 sockets closed" $named_stats |awk 'NR==1{print $1}'`
Socket_UDP_established=`grep "UDP/IPv4 connections established" $named_stats |awk 'NR==1{print $1}'`
Socket_TCP_established=`grep "TCP/IPv4 connections accepted" $named_stats |awk 'NR==1{print $1}'`
Socket_TCP_accepted=`grep "TCP/IPv4 recv errors" $named_stats |awk 'NR==1{print $1}'`
eval echo \$$1
