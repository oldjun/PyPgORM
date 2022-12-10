create table if not exists t_admin (
    id serial not null,
    username varchar(16) not null default '',
    phone varchar(16) not null default '',
    money decimal(10,2) not null default 0,
    role int not null default 0,
    time timestamp(0) without time zone not null default current_timestamp,
    primary key(id)
);