package com.equivoz.security;

import com.equivoz.repository.UserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;
import org.springframework.http.MediaType;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserRepository userRepository;

    public JwtAuthenticationFilter(JwtService jwtService, UserRepository userRepository) {
        this.jwtService = jwtService;
        this.userRepository = userRepository;
    }

    @Override
    protected boolean shouldNotFilter(@NonNull HttpServletRequest request) {
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            return true;
        }
        String path = request.getRequestURI();
        String method = request.getMethod();
        if (path.equals("/api/health")) {
            return true;
        }
        if (path.equals("/api/auth/register") && "POST".equals(method)) {
            return true;
        }
        if (path.equals("/api/auth/login") && "POST".equals(method)) {
            return true;
        }
        return path.equals("/api/denuncias/tipos-violacao") && "GET".equals(method);
    }

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain)
            throws ServletException, IOException {

        String header = request.getHeader("Authorization");
        if (header == null || !header.regionMatches(true, 0, "Bearer ", 0, 7)) {
            writeUnauthorized(response);
            return;
        }
        String token = header.substring(7).trim();
        if (!jwtService.isValid(token)) {
            writeUnauthorized(response, "Token inválido ou expirado");
            return;
        }
        String email = jwtService.extractEmail(token);
        var user = userRepository.findByEmail(email);
        if (user.isEmpty()) {
            writeUnauthorized(response, "Usuário não encontrado");
            return;
        }

        var auth = new UsernamePasswordAuthenticationToken(
                user.get(), null, List.of(new SimpleGrantedAuthority("ROLE_USER")));
        auth.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
        SecurityContextHolder.getContext().setAuthentication(auth);

        filterChain.doFilter(request, response);
    }

    private static void writeUnauthorized(HttpServletResponse response) throws IOException {
        writeUnauthorized(response, "Não autenticado");
    }

    private static void writeUnauthorized(HttpServletResponse response, String detail) throws IOException {
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding("UTF-8");
        response.getWriter().write("{\"detail\":\"" + escapeJson(detail) + "\"}");
    }

    private static String escapeJson(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
