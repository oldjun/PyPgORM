create table if not exists t_admin_auth (
    id serial not null,
    role int not null default 0,
    action varchar(8) not null default '',
    time timestamp(0) without time zone not null default current_timestamp,
    primary key(id)
);