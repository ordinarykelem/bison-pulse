-- Fix security issues from previous migration - correct order

-- 1. Drop trigger first, then function, then recreate both with proper search_path
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

-- Recreate function with SET search_path = public
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger 
LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public
AS $$
begin
  insert into public.profiles (user_id, email)
  values (new.id, new.email);
  return new;
end;
$$;

-- Recreate the trigger
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 2. Fix the purge function search path
DROP FUNCTION IF EXISTS public.purge_detections_older_than(int);
CREATE OR REPLACE FUNCTION public.purge_detections_older_than(days int)
RETURNS int 
LANGUAGE sql 
SECURITY DEFINER 
SET search_path = public
AS $$
  DELETE FROM public.detections
  WHERE ts < now() - (days || ' days')::interval;
  SELECT count(*)::int;
$$;

-- 3. Fix the security definer view by recreating it as a regular view
DROP VIEW IF EXISTS public.detections_last_15m;
CREATE VIEW public.detections_last_15m AS
SELECT *
FROM public.detections
WHERE ts >= now() - interval '15 minutes';