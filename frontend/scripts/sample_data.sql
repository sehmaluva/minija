-- Sample data for poultry management system
-- Run this after initial migrations

-- Insert sample breeds
INSERT INTO poultry_breed (id, name, breed_type, origin_country, description, average_weight_male, average_weight_female, egg_production_per_year, maturity_age_weeks, life_expectancy_years, created_at) VALUES
(gen_random_uuid(), 'Rhode Island Red', 'dual_purpose', 'United States', 'Hardy dual-purpose breed known for brown eggs', 3.9, 2.9, 250, 20, 8, NOW()),
(gen_random_uuid(), 'Leghorn', 'layer', 'Italy', 'Excellent white egg layer', 2.7, 2.0, 320, 18, 7, NOW()),
(gen_random_uuid(), 'Cornish Cross', 'broiler', 'United Kingdom', 'Fast-growing meat bird', 4.5, 3.6, 0, 8, 2, NOW()),
(gen_random_uuid(), 'Sussex', 'dual_purpose', 'England', 'Good forager and layer', 4.1, 3.2, 240, 22, 8, NOW()),
(gen_random_uuid(), 'New Hampshire', 'dual_purpose', 'United States', 'Good meat and egg production', 3.9, 2.9, 220, 21, 8, NOW());

-- Insert sample feed types
INSERT INTO management_feedtype (id, name, brand, feed_category, protein_percentage, energy_kcal_per_kg, cost_per_kg, description, created_at) VALUES
(gen_random_uuid(), 'Chick Starter', 'Premium Feeds', 'starter', 20.0, 2900, 45.00, 'High protein starter feed for chicks 0-6 weeks', NOW()),
(gen_random_uuid(), 'Grower Feed', 'Premium Feeds', 'grower', 16.0, 2850, 42.00, 'Balanced nutrition for growing birds 6-16 weeks', NOW()),
(gen_random_uuid(), 'Layer Pellets', 'Premium Feeds', 'layer', 16.5, 2750, 40.00, 'Complete nutrition for laying hens', NOW()),
(gen_random_uuid(), 'Broiler Finisher', 'Premium Feeds', 'finisher', 18.0, 3100, 44.00, 'High energy feed for meat birds', NOW()),
(gen_random_uuid(), 'Organic Layer', 'Natural Choice', 'layer', 17.0, 2700, 55.00, 'Certified organic layer feed', NOW());

-- Note: Actual farm, flock, and bird data should be created through the API
-- as it requires user authentication and proper relationships
