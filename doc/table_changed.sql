﻿alter table pbb.sppt add posted integer;
update pbb.sppt set posted = 0;
alter table pbb.sppt alter posted SET not null;
alter table pbb.sppt alter posted  SET DEFAULT 0;
