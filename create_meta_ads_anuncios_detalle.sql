create table public.meta_ads_anuncios_detalle (
  id serial not null,
  ad_id text not null,
  nombre_anuncio text null,
  importe_gastado numeric null,
  id_cuenta_publicitaria text not null,
  conjunto_id text null,
  campana_id text null,
  alcance integer null,
  impresiones integer null,
  interacciones integer null,
  mensajes integer null,
  clicks integer null default 0,
  link_clicks integer null default 0,
  inline_link_clicks integer null default 0,
  ctr numeric null,
  cpc numeric null,
  cost_per_unique_click numeric null,
  cost_per_unique_inline_link_click numeric null,
  unique_clicks integer null,
  unique_inline_link_clicks integer null,
  frequency numeric null,
  quality_ranking text null,
  engagement_rate_ranking text null,
  conversion_rate_ranking text null,
  video_plays integer null,
  video_plays_15s integer null,
  video_avg_watch_time_secs numeric null,
  video_completion_rate numeric null,
  post_reactions integer null,
  shares integer null,
  comments integer null,
  saves integer null,
  page_engagement integer null,
  messaging_conversations_started integer null,
  video_plays_at_25 integer null,
  video_plays_at_50 integer null,
  video_plays_at_75 integer null,
  video_plays_at_100 integer null,
  video_play_actions jsonb null,
  video_avg_time_watched_actions numeric null,
  post_engagement integer null,
  post_comments integer null,
  post_shares integer null,
  cost_per_messaging_conversation_started numeric null,
  cost_per_inline_link_click numeric null,
  unique_ctr numeric null,
  unique_impressions integer null,
  unique_link_clicks integer null,
  cost_per_unique_link_click numeric null,
  cost_per_click numeric null,
  cost_per_1k_impressions numeric null,
  cost_per_10_sec_video_view numeric null,
  cost_per_2_sec_continuous_video_view numeric null,
  cost_per_action_type numeric null,
  cost_per_estimated_ad_recallers numeric null,
  cost_per_outbound_click numeric null,
  cost_per_thruplay numeric null,
  cost_per_unique_outbound_click numeric null,
  estimated_ad_recallers integer null,
  estimated_ad_recall_rate numeric null,
  outbound_clicks integer null,
  outbound_clicks_ctr numeric null,
  thruplay_rate numeric null,
  thruplays integer null,
  unique_outbound_clicks integer null,
  website_ctr numeric null,
  website_purchase_roas numeric null,
  purchase_roas numeric null,
  actions jsonb null,
  fecha_inicio date not null,
  fecha_fin date not null,
  fecha_reporte date null,
  nombre_campana text null,
  nombre_conjunto text null,
  publisher_platform text not null,
  constraint meta_ads_anuncios_detalle_pkey primary key (
    ad_id,
    publisher_platform,
    fecha_inicio,
    fecha_fin
  ),
  constraint anuncios_detalle_unique unique (
    ad_id,
    publisher_platform,
    fecha_inicio,
    fecha_fin
  ),
  constraint fk_anuncios_cuenta foreign KEY (id_cuenta_publicitaria) references meta_ads_cuentas (id_cuenta_publicitaria)
) TABLESPACE pg_default;
