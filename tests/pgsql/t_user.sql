create table if not exists t_user (
    id serial not null,
    name varchar(16) not null default '',
    phone varchar(16) not null default '',
    money decimal(10,2) not null default 0,
    birth date,
    gender int not null default 0,
    status int not null default 0,
    brief text null,
    time timestamp(0) without time zone not null default current_timestamp,
    primary key(id)
);