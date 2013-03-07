drop table if exists participants;

create table participants (
  p_id integer primary key autoincrement,
  age string not null,
  gender string not null,
  nat_lang string not null,
  oth_lang string not null,
  years_eng integer not null,
  years_lived integer not null
);

drop table if exists answers;

create table answers (
  p_id integer primary key autoincrement,
  pcent_delimited_ans string
);