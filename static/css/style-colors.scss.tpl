{# ===== COLOR VARIABLES from Admin Settings ===== #}
{# These are overridable from Tienda Nube admin panel #}

$primary-color: {{ settings.primary_color | default: '#C96A2E' }};
$secondary-color: {{ settings.secondary_color | default: '#E8A87C' }};
$background-color: {{ settings.background_color | default: '#FAF5EF' }};
$text-color: {{ settings.text_color | default: '#2C2C2A' }};
$text-secondary: {{ settings.text_secondary_color | default: '#888780' }};

:root {
  --terracota: #{$primary-color};
  --durazno: #{$secondary-color};
  --crema: #{$background-color};
  --carbon: #{$text-color};
  --piedra: #{$text-secondary};
}
