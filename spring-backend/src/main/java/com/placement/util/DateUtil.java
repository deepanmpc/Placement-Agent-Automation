package com.placement.util;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Utility class for common date formatting operations.
 */
public final class DateUtil {

    private static final DateTimeFormatter DATE_FORMAT =
            DateTimeFormatter.ofPattern("yyyy-MM-dd");

    private static final DateTimeFormatter DATE_TIME_FORMAT =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private static final DateTimeFormatter DISPLAY_DATE_FORMAT =
            DateTimeFormatter.ofPattern("dd MMM yyyy");

    private static final DateTimeFormatter DISPLAY_DATE_TIME_FORMAT =
            DateTimeFormatter.ofPattern("dd MMM yyyy, hh:mm a");

    private static final DateTimeFormatter ISO_DATE_TIME_FORMAT =
            DateTimeFormatter.ISO_LOCAL_DATE_TIME;

    private DateUtil() {
        // Prevent instantiation
    }

    /**
     * Format LocalDate as "yyyy-MM-dd".
     */
    public static String formatDate(LocalDate date) {
        return date != null ? date.format(DATE_FORMAT) : null;
    }

    /**
     * Format LocalDateTime as "yyyy-MM-dd HH:mm:ss".
     */
    public static String formatDateTime(LocalDateTime dateTime) {
        return dateTime != null ? dateTime.format(DATE_TIME_FORMAT) : null;
    }

    /**
     * Format LocalDate for display as "dd MMM yyyy" (e.g. "14 Jun 2026").
     */
    public static String formatDisplayDate(LocalDate date) {
        return date != null ? date.format(DISPLAY_DATE_FORMAT) : null;
    }

    /**
     * Format LocalDateTime for display as "dd MMM yyyy, hh:mm a".
     */
    public static String formatDisplayDateTime(LocalDateTime dateTime) {
        return dateTime != null ? dateTime.format(DISPLAY_DATE_TIME_FORMAT) : null;
    }

    /**
     * Format LocalDateTime as ISO-8601 string.
     */
    public static String formatIso(LocalDateTime dateTime) {
        return dateTime != null ? dateTime.format(ISO_DATE_TIME_FORMAT) : null;
    }

    /**
     * Parse a "yyyy-MM-dd" string to LocalDate.
     */
    public static LocalDate parseDate(String dateStr) {
        return dateStr != null ? LocalDate.parse(dateStr, DATE_FORMAT) : null;
    }

    /**
     * Parse a "yyyy-MM-dd HH:mm:ss" string to LocalDateTime.
     */
    public static LocalDateTime parseDateTime(String dateTimeStr) {
        return dateTimeStr != null ? LocalDateTime.parse(dateTimeStr, DATE_TIME_FORMAT) : null;
    }

    /**
     * Get current timestamp formatted as "yyyy-MM-dd HH:mm:ss".
     */
    public static String nowFormatted() {
        return formatDateTime(LocalDateTime.now());
    }
}
