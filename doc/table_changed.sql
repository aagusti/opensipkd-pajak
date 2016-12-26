alter table pbb.sppt add posted integer;
update pbb.sppt set posted = 0;
alter table pbb.sppt alter posted SET not null;
alter table pbb.sppt alter posted  SET DEFAULT 0;
alter table pbb.skkpp add posted integer not null default 0;

update pbb.sppt_akrual set posted =0;



update pbb.pembayaran_sppt set posted =0;