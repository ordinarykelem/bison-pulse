-- Final fix for security definer view issue

-- Drop all views in public schema
DROP VIEW IF EXISTS public.detections_last_15m CASCADE;

-- Recreate the view with explicit security invoker (default) behavior
CREATE VIEW public.detections_last_15m 
WITH (security_invoker = true) AS
SELECT 
    id,
    ts,
    count,
    movement,
    fps,
    source,
    raw,
    created_by,
    created_at
FROM public.detections
WHERE ts >= now() - interval '15 minutes';