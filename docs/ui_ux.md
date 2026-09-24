# UI/UX.md — Product Interface and Experience Design Architecture

## 1. Executive Summary

Bhookh.exe is an ingredient-level food discovery interface engineered to eliminate uncertainty for diners with dietary restrictions, specific spice preferences, and ingredient allergies. 

This document defines the Minimum Viable Product user experience architecture across six core screens. It omits administrative operations and telephonic call capabilities, prioritizing digital transparency, frictionless discovery, and contextual, progressive authentication.

---

## 2. Core User Journey and Information Architecture

### 2.1 Complete Screen Navigation Flow

```mermaid
flowchart TD
    S1[Screen 1: Home and Discovery] -->|Execute Search or Select Filters| S2[Screen 2: Search Results]
    S1 -->|Bottom Navigation: Favourites Tab| S5[Screen 5: Favourites]
    
    S2 -->|Select Dish Card| S3[Screen 3: Dish Details]
    S2 -->|Select Heart Icon as Guest| S4[Screen 4: Authentication]
    
    S3 -->|Select Heart Icon as Guest| S4
    S3 -->|Select Heart Icon as Registered User| S3A[Optimistic State Update: Dish Favorited]
    S3 -->|Select Write Review as Guest| S4
    S3 -->|Select Write Review as Registered User| S6[Screen 6: Write Review]
    
    S4 -->|Successful Authentication| S3
    
    S5 -->|Select Saved Dish Card| S3
    S5 -->|Empty State Call to Action| S1
    
    S6 -->|Submit Review Successfully| S3