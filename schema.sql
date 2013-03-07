drop table if exists participants;

create table participants (
  r_id integer primary key autoincrement,
  user_id string not null,
  age string not null,
  gender string not null,
  nat_lang string not null,
  oth_lang string not null,
  years_eng string not null,
  years_eng_cnt string not null
);

drop table if exists answers;

create table answers (
  p_id integer primary key autoincrement,
  pcent_delim_ans string
);