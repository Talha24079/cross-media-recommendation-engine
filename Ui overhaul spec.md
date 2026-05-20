# CrossMedia — Complete UI/UX Overhaul Specification

> **Aesthetic Direction:** *Editorial Dark — a cinematic, magazine-grade entertainment platform.*
> Think: Letterboxd meets A24 meets Spotify's visual boldness. Rich depth, editorial typography,
> purposeful negative space, and a colour system with real personality.

---

## 1. Design System Tokens

### 1.1 Colour Palette

```dart
// lib/core/theme/app_colors.dart

class AppColors {
  // === BACKGROUNDS ===
  static const Color bgDeep       = Color(0xFF080B10); // True deep — not pure black
  static const Color bgBase       = Color(0xFF0F1218); // Main surface
  static const Color bgElevated   = Color(0xFF161C26); // Cards, panels
  static const Color bgOverlay    = Color(0xFF1E2636); // Hover/selected states
  static const Color bgGlass      = Color(0x1AFFFFFF); // Glass morphism overlays

  // === PRIMARY ACCENT — Electric Violet ===
  static const Color primary      = Color(0xFF7C5CFC); // Main CTA, active nav
  static const Color primaryLight = Color(0xFFAA8FFD); // Hover state
  static const Color primaryDim   = Color(0xFF3D2E7E); // Subtle tint backgrounds
  static const Color primaryGlow  = Color(0x407C5CFC); // Glow/shadow effect

  // === SECONDARY ACCENT — Ember Gold ===
  // (Keep this — it's your RP/economy colour and it works)
  static const Color gold         = Color(0xFFFFB800); // RP badges, streaks
  static const Color goldDim      = Color(0xFF3D2D00); // Gold tint bg

  // === TERTIARY — Neon Mint ===
  static const Color mint         = Color(0xFF00E5A0); // Match % bars, online dots
  static const Color mintDim      = Color(0xFF003D2B); // Mint tint bg

  // === SEMANTIC ===
  static const Color error        = Color(0xFFFF4D6A);
  static const Color warning      = Color(0xFFFFB800); // Same as gold
  static const Color success      = Color(0xFF00E5A0); // Same as mint

  // === TEXT ===
  static const Color textPrimary  = Color(0xFFF0F2F5); // Headlines
  static const Color textSecond   = Color(0xFF8B95A8); // Body / meta
  static const Color textMuted    = Color(0xFF4A5568); // Placeholder / disabled
  static const Color textInverse  = Color(0xFF080B10); // Text on light bg

  // === BORDERS ===
  static const Color borderSubtle = Color(0x14FFFFFF); // ~8% white
  static const Color borderMed    = Color(0x29FFFFFF); // ~16% white
  static const Color borderAccent = Color(0xFF7C5CFC); // Primary-coloured border

  // === CATEGORY COLOURS (for Media Type chips) ===
  static const Color catGame      = Color(0xFF7C5CFC); // Violet
  static const Color catMovie     = Color(0xFFFF6B6B); // Coral red
  static const Color catBook      = Color(0xFFFFB800); // Gold
  static const Color catMusic     = Color(0xFF00E5A0); // Mint
  static const Color catAnime     = Color(0xFFFF85C1); // Pink
  static const Color catPodcast   = Color(0xFF60AFFF); // Sky blue
}
```

---

### 1.2 Typography

```dart
// lib/core/theme/app_typography.dart
// Fonts to add to pubspec.yaml:
//   - Syne          (Display / headings — geometric, editorial)
//   - DM Sans       (Body — clean, readable, modern)

import 'package:flutter/material.dart';

class AppTypography {
  static const String displayFont = 'Syne';
  static const String bodyFont    = 'DM Sans';

  // DISPLAY
  static const TextStyle displayXL = TextStyle(
    fontFamily: displayFont,
    fontSize: 48, fontWeight: FontWeight.w800,
    letterSpacing: -1.5, height: 1.1,
    color: AppColors.textPrimary,
  );
  static const TextStyle displayL = TextStyle(
    fontFamily: displayFont,
    fontSize: 36, fontWeight: FontWeight.w700,
    letterSpacing: -1.0, height: 1.15,
    color: AppColors.textPrimary,
  );

  // HEADINGS
  static const TextStyle h1 = TextStyle(
    fontFamily: displayFont,
    fontSize: 28, fontWeight: FontWeight.w700,
    letterSpacing: -0.5, height: 1.2,
    color: AppColors.textPrimary,
  );
  static const TextStyle h2 = TextStyle(
    fontFamily: displayFont,
    fontSize: 22, fontWeight: FontWeight.w600,
    letterSpacing: -0.3, height: 1.25,
    color: AppColors.textPrimary,
  );
  static const TextStyle h3 = TextStyle(
    fontFamily: displayFont,
    fontSize: 18, fontWeight: FontWeight.w600,
    letterSpacing: -0.2, height: 1.3,
    color: AppColors.textPrimary,
  );

  // BODY
  static const TextStyle bodyL = TextStyle(
    fontFamily: bodyFont,
    fontSize: 16, fontWeight: FontWeight.w400,
    letterSpacing: 0.1, height: 1.6,
    color: AppColors.textSecond,
  );
  static const TextStyle bodyM = TextStyle(
    fontFamily: bodyFont,
    fontSize: 14, fontWeight: FontWeight.w400,
    letterSpacing: 0.1, height: 1.55,
    color: AppColors.textSecond,
  );
  static const TextStyle bodyS = TextStyle(
    fontFamily: bodyFont,
    fontSize: 12, fontWeight: FontWeight.w400,
    letterSpacing: 0.2, height: 1.5,
    color: AppColors.textMuted,
  );

  // LABELS / UI
  static const TextStyle labelL = TextStyle(
    fontFamily: bodyFont,
    fontSize: 14, fontWeight: FontWeight.w600,
    letterSpacing: 0.5,
    color: AppColors.textPrimary,
  );
  static const TextStyle labelM = TextStyle(
    fontFamily: bodyFont,
    fontSize: 12, fontWeight: FontWeight.w600,
    letterSpacing: 0.8,
    color: AppColors.textSecond,
  );
  static const TextStyle labelS = TextStyle(
    fontFamily: bodyFont,
    fontSize: 11, fontWeight: FontWeight.w700,
    letterSpacing: 1.2,
    color: AppColors.textMuted,
  );

  // OVERLINE (section headers like "TRENDING NOW")
  static const TextStyle overline = TextStyle(
    fontFamily: bodyFont,
    fontSize: 11, fontWeight: FontWeight.w700,
    letterSpacing: 2.0,
    color: AppColors.textMuted,
  );
}
```

---

### 1.3 Spacing & Shape Tokens

```dart
// lib/core/theme/app_dimensions.dart

class AppDimensions {
  // SPACING (8pt grid)
  static const double xs  = 4.0;
  static const double sm  = 8.0;
  static const double md  = 16.0;
  static const double lg  = 24.0;
  static const double xl  = 32.0;
  static const double xxl = 48.0;
  static const double xxxl = 64.0;

  // PAGE PADDING
  static const double pagePadH = 20.0;   // Mobile horizontal padding
  static const double pagePadV = 16.0;   // Mobile vertical padding

  // BORDER RADIUS
  static const double radiusXS  = 4.0;
  static const double radiusSM  = 8.0;
  static const double radiusMD  = 12.0;
  static const double radiusLG  = 16.0;
  static const double radiusXL  = 24.0;
  static const double radiusXXL = 32.0;
  static const double radiusFull = 999.0;

  // CARD SIZES
  static const double mediaCardWidth  = 120.0;  // Portrait card (home row)
  static const double mediaCardHeight = 180.0;
  static const double trendingCardH   = 220.0;  // Trending wide cards

  // BOTTOM NAV
  static const double bottomNavHeight = 68.0;
  static const double bottomNavIndicatorSize = 44.0;
}
```

---

### 1.4 Effects & Shadows

```dart
// lib/core/theme/app_effects.dart

class AppEffects {
  // CARD SHADOWS
  static List<BoxShadow> get cardShadow => [
    BoxShadow(
      color: Colors.black.withOpacity(0.4),
      blurRadius: 24, offset: const Offset(0, 8),
    ),
  ];

  static List<BoxShadow> get cardShadowHover => [
    BoxShadow(
      color: AppColors.primaryGlow,
      blurRadius: 32, offset: const Offset(0, 12),
    ),
    BoxShadow(
      color: Colors.black.withOpacity(0.5),
      blurRadius: 20, offset: const Offset(0, 6),
    ),
  ];

  // GLOW EFFECTS
  static List<BoxShadow> get primaryGlow => [
    BoxShadow(
      color: AppColors.primaryGlow,
      blurRadius: 20, spreadRadius: -4,
    ),
  ];

  static List<BoxShadow> get goldGlow => [
    BoxShadow(
      color: AppColors.gold.withOpacity(0.35),
      blurRadius: 20, spreadRadius: -4,
    ),
  ];

  // GLASS MORPHISM DECORATION
  static BoxDecoration get glassCard => BoxDecoration(
    color: AppColors.bgElevated,
    borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
    border: Border.all(color: AppColors.borderSubtle, width: 1),
    boxShadow: cardShadow,
  );

  static BoxDecoration get glassPrimary => BoxDecoration(
    color: AppColors.primaryDim,
    borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
    border: Border.all(color: AppColors.primary.withOpacity(0.3), width: 1),
  );
}
```

---

## 2. Complete ThemeData

```dart
// lib/core/theme/app_theme.dart

import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'app_typography.dart';
import 'app_dimensions.dart';

class AppTheme {
  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: AppColors.bgDeep,
    primaryColor: AppColors.primary,
    colorScheme: const ColorScheme.dark(
      primary: AppColors.primary,
      secondary: AppColors.gold,
      tertiary: AppColors.mint,
      surface: AppColors.bgElevated,
      background: AppColors.bgBase,
      error: AppColors.error,
      onPrimary: Colors.white,
      onSecondary: AppColors.textInverse,
      onSurface: AppColors.textPrimary,
      onBackground: AppColors.textPrimary,
      outline: AppColors.borderSubtle,
    ),

    // TYPOGRAPHY
    textTheme: TextTheme(
      displayLarge:  AppTypography.displayXL,
      displayMedium: AppTypography.displayL,
      headlineLarge: AppTypography.h1,
      headlineMedium: AppTypography.h2,
      headlineSmall: AppTypography.h3,
      bodyLarge:  AppTypography.bodyL,
      bodyMedium: AppTypography.bodyM,
      bodySmall:  AppTypography.bodyS,
      labelLarge:  AppTypography.labelL,
      labelMedium: AppTypography.labelM,
      labelSmall:  AppTypography.labelS,
    ),

    // APP BAR
    appBarTheme: AppBarTheme(
      backgroundColor: AppColors.bgDeep,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
      titleTextStyle: AppTypography.h2.copyWith(
        fontFamily: 'Syne', fontWeight: FontWeight.w800,
      ),
      iconTheme: const IconThemeData(color: AppColors.textPrimary),
    ),

    // BOTTOM NAV
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: AppColors.bgBase,
      selectedItemColor: AppColors.primary,
      unselectedItemColor: AppColors.textMuted,
      showSelectedLabels: true,
      showUnselectedLabels: true,
      type: BottomNavigationBarType.fixed,
      elevation: 0,
      selectedLabelStyle: AppTypography.labelS,
      unselectedLabelStyle: AppTypography.labelS,
    ),

    // CARDS
    cardTheme: CardTheme(
      color: AppColors.bgElevated,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppDimensions.radiusLG),
        side: const BorderSide(color: AppColors.borderSubtle, width: 1),
      ),
    ),

    // INPUT / SEARCH
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.bgElevated,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppDimensions.radiusXL),
        borderSide: const BorderSide(color: AppColors.borderSubtle),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppDimensions.radiusXL),
        borderSide: const BorderSide(color: AppColors.borderSubtle),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppDimensions.radiusXL),
        borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
      ),
      hintStyle: AppTypography.bodyM.copyWith(color: AppColors.textMuted),
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      prefixIconColor: AppColors.textMuted,
    ),

    // CHIPS
    chipTheme: ChipThemeData(
      backgroundColor: AppColors.bgOverlay,
      selectedColor: AppColors.primaryDim,
      labelStyle: AppTypography.labelM,
      side: const BorderSide(color: AppColors.borderSubtle),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
    ),

    // ELEVATED BUTTON (Primary CTA)
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        minimumSize: const Size(0, 48),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
        ),
        textStyle: AppTypography.labelL,
        elevation: 0,
      ),
    ),

    // OUTLINED BUTTON
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.textPrimary,
        minimumSize: const Size(0, 48),
        side: const BorderSide(color: AppColors.borderMed),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
        ),
        textStyle: AppTypography.labelL,
      ),
    ),

    // FAB
    floatingActionButtonTheme: FloatingActionButtonThemeData(
      backgroundColor: AppColors.primary,
      foregroundColor: Colors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppDimensions.radiusXL),
      ),
    ),

    // DIVIDER
    dividerTheme: const DividerThemeData(
      color: AppColors.borderSubtle,
      thickness: 1,
      space: 0,
    ),

    // LIST TILE
    listTileTheme: ListTileThemeData(
      tileColor: Colors.transparent,
      iconColor: AppColors.textSecond,
      titleTextStyle: AppTypography.bodyL.copyWith(color: AppColors.textPrimary),
      subtitleTextStyle: AppTypography.bodyS,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
      ),
    ),
  );
}
```

---

## 3. Bottom Navigation — Redesign

### Current Problems
- Active pill (gold oval) looks inconsistent and cheap
- Icons are too small and unlabeled when inactive
- No visual separation from content

### New Design Spec

```dart
// lib/features/shell/widgets/app_bottom_nav.dart
// Replace the current bottom nav with this design:

/*
VISUAL SPEC:
- Background: AppColors.bgBase with a top border (borderSubtle)
- Height: 68px
- Active item: Violet pill (primaryDim bg) with primary-coloured icon + label
- Inactive item: Muted icon + muted label, no background
- Remove the gold oval entirely — use violet for ALL active states
- Add a thin violet underline glow on the active item

LAYOUT:
  [  Home  ] [  Discover  ] [  Economy  ] [  Community  ] [  Profile  ]
  Each item:
    - Icon: 22px
    - Label: 10px, letterSpacing 0.8, fontWeight 600
    - Active pill: 72px wide, 36px tall, radius 18, color primaryDim
    - Active icon + label: primary colour
    - Inactive icon + label: textMuted colour
*/
```

---

## 4. Screen-by-Screen Redesign

---

### 4.1 HOME SCREEN — Complete Rebuild from Scratch

#### ❌ Problems with Current Design
- "Personalized for You" is a plain horizontal card scroll with no visual identity
- "Trending Now" has NO content filtering — adult/inappropriate content appears (CRITICAL BUG)
- Large trending cards have no text overlay hierarchy
- No greeting, no personality, no sense of the user being "seen"
- "Top Picks by Category" section is inconsistently sized and unfinished

#### ✅ New Home Screen Layout

```
┌─────────────────────────────────────────────────────┐
│  HEADER                                             │
│  "Good evening, Talha"        [T]  [⚡ 42 RP]      │
│  "Your taste universe awaits"                       │
├─────────────────────────────────────────────────────┤
│  ━━━ YOUR TASTE ISLANDS ━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                     │
│  Horizontally scrollable "island" cards:            │
│                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────┐│
│  │  🎮 GAMES    │ │  🎬 MOVIES   │ │  📚 BOOKS   ││
│  │              │ │              │ │             ││
│  │  [cover art] │ │  [cover art] │ │  [cover art]││
│  │  [cover art] │ │  [cover art] │ │  [cover art]││
│  │              │ │              │ │             ││
│  │  3 matches   │ │  5 matches   │ │  2 matches  ││
│  └──────────────┘ └──────────────┘ └─────────────┘│
│  (each island tappable → filtered Discover view)   │
│                                                     │
├─────────────────────────────────────────────────────┤
│  ━━━ TRENDING IN YOUR COMMUNITY ━━━━━━━━━━━━━━━━━  │
│  [Only show items from YOUR database — no external] │
│                                                     │
│  Large card (2:3 ratio, full bleed image):         │
│  ┌─────────────────────────────────────────────┐   │
│  │                                             │   │
│  │          [cover image]                      │   │
│  │                                             │   │
│  │  ████████████████████                       │   │
│  │  Title of Media                  GAME chip  │   │
│  │  ★ 4.3   •  67% match                      │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Row of 3 smaller cards below (equal width)        │
│                                                     │
├─────────────────────────────────────────────────────┤
│  ━━━ TOP BY CATEGORY ━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                     │
│  Horizontal tab row: [Game] [Movie] [Book] [Anime] │
│  (switches the card grid below without page reload)│
│                                                     │
│  3-column grid of portrait cards                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### Taste Islands — Detailed Component Spec

```dart
/*
ISLAND CARD WIDGET SPEC:
- Size: 160px wide × 200px tall
- Background: gradient from categoryColor.withOpacity(0.15) to bgElevated
- Border: 1px categoryColor.withOpacity(0.3)
- Border radius: 20px
- Content:
    TOP: Category icon (emoji or Lucide icon) in a pill badge
         Category name in h3 (Syne, bold)
    MIDDLE: Stack of 2-3 mini cover thumbnails (50px wide each)
            overlapping like a hand of cards, with slight rotation
            (-3°, 0°, +3°)
    BOTTOM: "X top matches" label in mint colour
            Subtle arrow icon →

- On tap: Navigate to Discover with category pre-filtered
- Animation: gentle float on hover (web), scale on press (mobile)
*/
```

#### Trending Cards — Detailed Component Spec

```dart
/*
TRENDING CARD SPEC:
- Full bleed cover image (fill the card, no letter-boxing)
- Gradient overlay: transparent → black (bottom 60% of card)
- On the overlay:
    - Category chip (top-left corner, coloured by category)
    - Heart/save button (top-right corner, glass bg)
    - Title: h2, Syne bold, white, bottom-left
    - Match % + star rating: bodyM, mint for %, gold star for rating
- Border radius: 16px
- NO inappropriate content: implement in backend, see Section 7
*/
```

---

### 4.2 DISCOVER SCREEN

#### ❌ Problems
- "DISCOVER" header in uppercase serif looks generic
- Category chips are visually flat — no colour coding by type
- Match % progress bar is thin and colourless (grey track)
- List item cards look identical regardless of media type
- Search bar is functional but boring

#### ✅ New Discover Design

```
HEADER: Remove "DISCOVER" text. Search bar IS the header.
        Search bar sits sticky at top with blur backdrop.

SEARCH BAR:
- Background: bgElevated (slightly lighter)
- Border: borderSubtle at rest, primary at focus
- Leading: violet search icon
- Height: 52px, borderRadius: full
- Trailing: clear button when text present
- Placeholder: "Search movies, games, books..."

CATEGORY CHIPS (below search):
- Horizontally scrollable, no wrap
- Each chip colour-coded:
    All    → primary/violet bg when selected
    Movie  → coral red (#FF6B6B)
    Book   → gold (#FFB800)
    Game   → violet (#7C5CFC)
    Music  → mint (#00E5A0)
    Anime  → pink (#FF85C1)
    Podcast → sky (#60AFFF)
- Unselected: bgOverlay bg, coloured text, coloured left border
- Selected: solid coloured bg, white text
- Pill shape (borderRadius: full)

RESULT CARDS:
- Remove the flat rectangular card
- New design: horizontal card with:
    LEFT: Square thumbnail (72×72), borderRadius 10, with coloured 
          category border (3px left accent bar)
    CENTER:
        Title: h3, white, bold
        Category chip: 1-2 tags max (truncate rest as "+N")
        Star rating: gold stars (inline)
    RIGHT:
        Heart button (icon only)
        Match % as a circle badge:
            - Circular progress ring (mint colour)
            - % number in center (bold, small)
- Match progress bar: REMOVE the flat bar.
  Replace with the circular progress ring on the right side.
- Card background: bgElevated, border: borderSubtle
- Hover: border becomes primary colour, slight translateX(-2px)
```

---

### 4.3 ECONOMY SCREEN

#### ❌ Problems
- Page is extremely empty and undesigned
- "Claim Daily Streak" button is just an outline — looks inactive
- "Open Bounties" section is a blank void
- The RP balance is buried in the top-right corner

#### ✅ New Economy Design

```
HERO CARD (replaces the flat top card):
┌─────────────────────────────────────────────────────┐
│  Background: gradient mesh (primaryDim → goldDim)   │
│  Border: 1px primary.withOpacity(0.3)               │
│  BorderRadius: 20px                                 │
│                                                     │
│  LEFT:                                              │
│  "talha06"  (h2, Syne, white)                       │
│  "Reputation Points"  (labelS, muted)               │
│                                                     │
│  CENTER: Large RP number                            │
│  ⚡ 42  (displayL, gold, Syne bold)                 │
│  "RP Balance"  (bodyS, muted)                       │
│                                                     │
│  RIGHT: Small rank badge (if applicable)            │
└─────────────────────────────────────────────────────┘

DAILY STREAK BUTTON — New Design:
- Filled button, NOT outlined
- Background: goldDim, border: gold, text: gold
- Icon: 🔥 animated flicker (CSS/Flutter animation)
- Label: "Claim Daily Streak  •  +10 RP"
- When claimed: greys out, shows "Come back tomorrow"
- Height: 52px, borderRadius: 14px

STATS ROW (add this — currently missing):
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Bounties │  │  Answered│  │  Earned  │
│    0      │  │    0     │  │  0 RP    │
│  Posted   │  │          │  │  total   │
└──────────┘  └──────────┘  └──────────┘
Each stat: bgElevated card, number in h2 violet, label in bodyS muted

OPEN BOUNTIES SECTION:
- If empty: Illustrated empty state
    Icon: 🎯 (large, 64px)
    Title: "No open bounties yet"  (h3)
    Body: "Post a bounty to get recommendations from the community"
    CTA button: "+ Post a Bounty" (primary filled)
    Remove the current text-only empty state entirely

FAB (+ Bounty):
- Keep the FAB but change colour to primary (violet)
- Label: "+ Post Bounty"
- Position: bottom-right
```

---

### 4.4 COMMUNITY SCREEN

#### ❌ Problems
- "UNASSIGNED" faction banner is styled inconsistently (teal text, muted bg)
- Discussion threads look like a plain list — no visual hierarchy
- Avatar circles are just letter initials with flat dark bg
- No engagement metrics (reply count, views)
- The "+" Thread FAB is gold — inconsistent with primary violet

#### ✅ New Community Design

```
FACTION BANNER — Redesign:
┌─────────────────────────────────────────────────────┐
│  Background: subtle gradient, border: primary.30%   │
│  LEFT: Faction icon (🌐 for Unassigned)             │
│  CENTER:                                            │
│    "No Faction Yet"  (h3, white)                    │
│    "Interact with more media to join one"           │
│  RIGHT: Progress ring showing XP toward next rank   │
└─────────────────────────────────────────────────────┘

SECTION HEADER: "DISCUSSIONS"
- Remove the subtitle "Live updates via WebSocket. Pull down to reload."
- Replace with a small green dot + "Live" badge (top right of section header)

THREAD CARDS — Redesign:
┌─────────────────────────────────────────────────────┐
│  LEFT: Avatar circle                                │
│    - Gradient background (from primary to primaryL) │
│    - Initial letter, white bold                     │
│    - 40px diameter                                  │
│                                                     │
│  CENTER:                                            │
│    Title: bodyL, white, bold (NOT h2 — too large)  │
│    Preview: bodyS, textSecond (1 line, ellipsis)   │
│    Meta row: "Author · Date · 💬 N replies"        │
│                                                     │
│  RIGHT: →  chevron icon (textMuted)                 │
└─────────────────────────────────────────────────────┘
- Card bg: bgElevated
- Hover: bg becomes bgOverlay, left border 3px primary
- Animate in with stagger delay (each card 50ms later)

FAB: Change to PRIMARY VIOLET (not gold) for consistency
```

---

### 4.5 PROFILE SCREEN

#### ❌ Problems
- Avatar is a tiny dark circle with initial — very bare
- Username/email are styled inconsistently (gold vs white)
- "FAVORITE TASTE SEEDS" and "CONTRIBUTE MEDIA" sections are very empty
- Outlined buttons feel like placeholders, not real UI
- No sense of achievement or progress

#### ✅ New Profile Design

```
PROFILE HEADER CARD:
┌─────────────────────────────────────────────────────┐
│  Background: gradient mesh (primaryDim + bgElevated)│
│                                                     │
│  TOP ROW:                                           │
│    [Avatar — 72px, gradient ring, initial letter]   │
│    "TALHA06"  (h1, Syne bold, white)                │
│    email  (bodyS, muted)                            │
│                                                     │
│  STATS ROW:                                         │
│    ⚡ 42 RP  |  🗓 Member since May 2026  |  🎯 0 Bounties │
│    (each separated by a muted vertical divider)     │
└─────────────────────────────────────────────────────┘

AVATAR:
- 72px circle
- Background: gradient (primary → primaryLight)
- Ring: 2px gap + 2px primary border (like Instagram)
- Initial: displayL, white

TASTE SEEDS SECTION:
- Section header: overline style ("YOUR TASTE DNA")
- Chips redesign:
    Background: bgOverlay
    Border: category colour (game=violet, movie=red, etc.)
    Close button: small X in textMuted
    Tag label includes emoji prefix: 🎮 Tomb Raider (game)
- "Add favorite title" → filled outlined button:
    Icon: ♥
    Text: "Add a Title"
    Style: outlined, borderColor: primary, textColor: primary
    Height: 44px, radius: full

CONTRIBUTE MEDIA SECTION:
- Header: overline ("CONTRIBUTE & EARN")
- Card instead of outlined button:
  ┌──────────────────────────────────────────────────┐
  │  LEFT: ⊕ icon in gold circle                    │
  │  CENTER: "Add Media to Catalog"  (labelL, white) │
  │          "Earn +5 RP per approved entry"         │
  │  RIGHT: → chevron                                │
  └──────────────────────────────────────────────────┘
  Background: goldDim, border: gold.withOpacity(0.3)

LOGOUT BUTTON (top-right):
- Replace the current icon with a ghost button: 
  "Log out" text + exit icon, color: error
```

---

## 5. Shared Widget Redesigns

### 5.1 MediaCard (media_card.dart)

```dart
/*
PORTRAIT CARD (used in Home rows, Category grids):
- Width: 120px, Height: 180px (3:2 poster ratio)
- ClipRRect radius: 12px
- Image: BoxFit.cover (fill — no letterboxing)
- Gradient overlay: bottom 50%, black 0.8 opacity
- On overlay:
    - Title: bodyS, white, bold, max 2 lines
    - Match %: labelS, mint, with % sign
- On hover (web): scale 1.02, border primary 1.5px
- Loading: Shimmer placeholder (dark animated gradient)
- Error fallback: grey card with category icon centered
*/
```

### 5.2 AppScaffold (app_scaffold.dart)

```dart
/*
- backgroundColor: AppColors.bgDeep (NOT bgBase, deeper)
- No SafeArea on top (let content go edge to edge)
- SafeArea on bottom (respect nav bar)
- extendBody: true (content goes behind bottom nav)
- Page padding: 20px horizontal applied per-page, not here
*/
```

### 5.3 ReputationBadge (reputation_badge.dart)

```dart
/*
CURRENT: Gold oval pill with ⚡ and "42 RP"
KEEP THIS — it works. Minor tweaks only:
- Border radius: 999 (fully pill)
- Background: goldDim (Color(0xFF3D2D00))
- Border: gold.withOpacity(0.4)
- Icon: ⚡ in gold, 14px
- Text: "42 RP" in gold, labelM, bold
- BoxShadow: goldGlow (from AppEffects)
*/
```

### 5.4 UserAvatar (user_avatar.dart)

```dart
/*
SIZE VARIANTS: sm (28px), md (40px), lg (72px)

DESIGN:
- Circle with gradient background:
    LinearGradient(colors: [primary, primaryLight], 
                   begin: Alignment.topLeft, end: Alignment.bottomRight)
- Initial letter: white, bold, sized proportionally
- RING (for lg only): 
    Container with 2px transparent gap + 2px primary border
- If has image: ClipOval with NetworkImage, keep ring

ONLINE DOT (for community context):
- 10px circle, mint colour, bottom-right of avatar
- White 2px border around the dot
*/
```

### 5.5 LoadingView (loading_view.dart)

```dart
/*
REPLACE generic spinner with:
- Centered column
- Animated logo mark (your app's first letter in Syne, 48px)
- 3 animated dots below (bounce animation, staggered)
- Colours: primary, primaryLight, primary (dots)
- Subtle: "Loading..." in bodyS muted below the dots
*/
```

### 5.6 ErrorBanner (error_banner.dart)

```dart
/*
DESIGN:
- Background: Color(0xFF2D0F14)  (dark red tint)
- Border: error.withOpacity(0.4), left: 3px error solid
- Border radius: 10px
- Icon: ⚠ in error colour, 20px
- Message text: bodyM, error light colour
- Optional retry button: text button, error colour
*/
```

### 5.7 AppFormDialog (app_form_dialog.dart)

```dart
/*
DESIGN:
- Background: bgElevated
- Border radius: 20px
- Border: borderMed
- Header: h2 Syne title + X close button (top-right)
- Divider below header: borderSubtle
- Body: 20px padding
- Action row: right-aligned, Cancel (text btn) + Submit (filled primary)
- Backdrop: black.withOpacity(0.7) + blur(12)
*/
```

---

## 6. Content Safety — CRITICAL FIX

### The Problem
The recommendation algorithm is surfacing adult/explicit content (e.g., explicit anime titles appeared in the Trending Now section). This is a critical issue that must be fixed **before any UI work**.

### Fix Locations

**Backend (API layer):**
```
lib/data/api/  — Add a content filter to all media fetch endpoints

Add a blocklist check OR a content rating filter:
- Only return items where content_rating NOT IN ['adult', 'explicit', 'nsfw', 'xxx', 'hentai']
- OR: Add an `is_safe_for_all` boolean flag to your media model and filter on it
- The Trending Now endpoint especially must enforce this filter
```

**Frontend (defensive layer):**
```dart
// lib/data/models/media_item.dart
// Add this getter:
bool get isSafeContent {
  final blockedKeywords = ['porn', 'hentai', 'xxx', 'explicit', 'nsfw', 'adult'];
  final titleLower = title.toLowerCase();
  return !blockedKeywords.any((word) => titleLower.contains(word));
}

// lib/data/providers/ — In your home/trending providers:
final safeItems = allItems.where((item) => item.isSafeContent).toList();
```

**Note:** The frontend filter is a safety net only. Fix it at the data/API level as the primary solution.

---

## 7. Implementation Priority Order

```
PHASE 1 — Foundation (do first, everything depends on this)
  ✅ app_colors.dart          — New colour tokens
  ✅ app_typography.dart      — New font system (add Syne + DM Sans to pubspec)
  ✅ app_dimensions.dart      — Spacing/shape tokens
  ✅ app_effects.dart         — Shadow/glow effects
  ✅ app_theme.dart           — Wire it all into ThemeData

PHASE 2 — Critical Bug Fix
  🚨 Content filter in API/providers layer (NSFW content appearing)

PHASE 3 — Shell & Navigation
  ✅ app_scaffold.dart        — Background & body extension
  ✅ Bottom nav bar           — Violet active state, remove gold oval

PHASE 4 — Shared Widgets
  ✅ reputation_badge.dart    — Minor tweaks
  ✅ user_avatar.dart         — Gradient ring avatar
  ✅ media_card.dart          — Full redesign
  ✅ loading_view.dart        — New animated loading
  ✅ error_banner.dart        — Styled error state
  ✅ app_form_dialog.dart     — Glassmorphism dialog

PHASE 5 — Screens (in this order)
  ✅ home                     — FULL REBUILD (taste islands, new trending)
  ✅ discover                 — Coloured chips, circular match, new cards
  ✅ profile                  — Hero card, taste DNA section
  ✅ economy                  — Hero card, stats row, empty state
  ✅ community                — Thread cards, faction banner
```

---

## 8. pubspec.yaml Changes Required

```yaml
fonts:
  - family: Syne
    fonts:
      - asset: assets/fonts/Syne-Regular.ttf
      - asset: assets/fonts/Syne-Medium.ttf   weight: 500
      - asset: assets/fonts/Syne-SemiBold.ttf weight: 600
      - asset: assets/fonts/Syne-Bold.ttf     weight: 700
      - asset: assets/fonts/Syne-ExtraBold.ttf weight: 800
  - family: DM Sans
    fonts:
      - asset: assets/fonts/DMSans-Regular.ttf
      - asset: assets/fonts/DMSans-Medium.ttf  weight: 500
      - asset: assets/fonts/DMSans-SemiBold.ttf weight: 600
      - asset: assets/fonts/DMSans-Bold.ttf    weight: 700

# Alternative: Use google_fonts package instead of bundling:
dependencies:
  google_fonts: ^6.2.1
# Then in AppTypography: GoogleFonts.syne(...), GoogleFonts.dmSans(...)
```

---

## 9. Quick Visual Summary

| Element | Before | After |
|---|---|---|
| Primary accent | Gold/yellow | Electric Violet #7C5CFC |
| Secondary accent | Teal/cyan | Ember Gold #FFB800 (keep for RP only) |
| Background | Flat #000 / #0D1117 | Layered depth: #080B10 → #161C26 |
| Font | System default | Syne (display) + DM Sans (body) |
| Home personalisation | Horizontal card scroll | Category "Taste Islands" |
| Trending section | Random / unfiltered | DB-only, filtered, editorial layout |
| Match indicator | Thin progress bar | Circular progress ring |
| Category chips | Plain grey, uniform | Colour-coded by media type |
| Buttons | Mixed gold/teal outline | Violet primary, consistent system |
| Cards | Flat dark rectangle | Depth, shadows, hover glow |
| Empty states | Plain text | Illustrated with CTA |
| Content safety | None | API filter + frontend blocklist |
```