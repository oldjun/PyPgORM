create table if not exists t_admin_role (
    id serial not null,
    name varchar(16) not null default '',
    time timestamp(0) without time zone not null default current_timestamp,
    primary key(id)
);