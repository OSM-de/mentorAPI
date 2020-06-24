# SQL Snippets for playing around

## Add complete new user

```sql
insert into profiles
values ('osm_56464',Null,Null,Null,Null,Null,Null,Null,Null);
```

Here: `osm_65464` is just an example. Replace it with any value you want in the format `osm_<unique identifier>`

## Remove user

```sql
delete from profiles where id=%s;
```

### Update

#### Text Direction of user

```sql
update profiles set textdirection=%s where id=%s;
```

#### Location of user

```sql
update profiles set location=%s where id=%s;
```

`location` in the format of e.g. `de,sh,hu` (Germany,Schleswig-Holstein,Henstedt-Ulzburg (do not use the long version))

#### Display Name

```sql
update profiles set displayname=%s where id=%s;
```

#### Add language

```sql
update profiles set languages=%s where id=%s;
```

**Not complete:** This query won't work. The `languages` column is an array and I did not add a logic for removing/adding of array items yet. I also did not add a logic for removing certain user data, only changing them.

#### Add contact

```sql
update profiles set contact=%s where id=%s;
```

**Not complete:** This query won't work. The `contact` column is a jsonb and I did not add a logic for removing/adding of jsonb key-value pairs yet. I also did not add a logic for removing certain user data, only changing them.

#### Add keywords

```sql
update profiles set keywords=%s where id=%s;
```

**Not complete:** This query won't work. The `keywords` column is an array and I did not add a logic for removing/adding of array items yet. I also did not add a logic for removing certain user data, only changing them.

#### Add a bio

```sql
update profiles set about=%s where id=%s;
```

#### Toggle availability

```sql
update profiles set available=%s where id=%s;
```

## See more

Head over to [../lib/database.py](../lib/database.py) for a complete and up to data version of all queries. Not listet all here since this file is for demonstration purpose only.
